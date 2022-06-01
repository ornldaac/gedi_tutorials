#!/usr/bin/env python3
import argparse
import http.cookiejar
import pathlib
import requests
import sys
import datetime as dt
import geopandas as gpd
import netCDF4 as nc
import pandas as pd
from os import path
from shapely.ops import orient
from urllib.parse import urlsplit
from requests.adapters import HTTPAdapter, Retry
import warnings
warnings.filterwarnings('ignore')

DT_FORMAT = "%Y-%m-%d"
CMR_URL="https://cmr.earthdata.nasa.gov/search/"
AUTH_HOST = "https://urs.earthdata.nasa.gov"
HEADERS = ['lat_lowestmode', 'lon_lowestmode', 'elev_lowestmode', 'shot_number']

def parse_args(args):
    """Parses command line agruments."""

    parser = argparse.ArgumentParser(
        description="Access GEDI L4A using NASA OPeNDAP in the Cloud",
        usage="gedi_l4a_hyrax.py --doi <DOI> --date1 <start_date> --date2 <end_date> --poly <path_to_geojson_file> --beams <gedi_beams> --variables <gedi_variables> --outfile <output_csv_file> [--json]\n"
    )
    parser.add_argument(
        "--doi",
        required=True, 
        type=check_doi, 
        help="DOI e.g., 10.3334/ORNLDAAC/2056 for GEDI L4A V2.1"
    )
    parser.add_argument(
        "--date1",
        required=True, 
        type=check_datefmt,
        help="start date in YYYY-MM-DD format"
    )
    parser.add_argument(
        "--date2",
        required=True, 
        type=check_datefmt,
        help="end date in YYYY-MM-DD format"
    )
    parser.add_argument(
        "--poly",
        required=True, 
        type=argparse.FileType('r', encoding='UTF-8'), 
        help="path to a GeoJSON file defining area of interest"
    )
    parser.add_argument(
        "--beams",
        required=True, 
        type=lambda arg: arg.split(','), 
        help="GEDI beam names in a comma-separated format"
    )
    parser.add_argument(
        "--variables",
        required=True, 
        type=lambda arg: arg.split(','), 
        help="GEDI variable names in a comma-separated format"
    )
    parser.add_argument(
        "--outfile",
        required=True,
        type=pathlib.Path,
        help="output CSV file name"
    )
    parser.add_argument(
        "--json",
        default=False,
        action='store_true',
        help="setting this creates additional output GeoJSON subset file"
    )

    return parser.parse_args(args)

def check_datefmt(d: str):
    """Checks if date parameters are in correct format.
    
    Args:
        d (str): date string in YYYY-MM-DD
    
    Returns:
        datetime object
    """
    try:
        return dt.datetime.strptime(d, DT_FORMAT)
    except ValueError:
        msg = "not a valid date in YYYY-MM-DD format"
        raise argparse.ArgumentTypeError(msg)

def check_doi(d: str):
    """Checks if DOI passed is valid and the dataset exists at NASA CMR
    
    Args:
        d (str): DOI
    
    Returns:
        string: DOI stripped off https://doi.org, if any
    """
    try:
        dpath = urlsplit(d).path.strip("/")
        requests.get(CMR_URL + 'collections.json?doi=' + dpath).json()['feed']['entry'][0]['id']
        return dpath
    except (ValueError, IndexError):
        msg = "not a valid DOI"
        raise argparse.ArgumentTypeError(msg)

def get_granules_hyrax(doi: str, poly_epsg4326, temporal_str: str):
    """Get hyrax url for the granules that overlaps the temporal and 
    spatial bounds.
    
    Args:
        doi (str): dataset DOI
        poly_epsg4326: GeoDataFrame object containing the polygon object
        temporal_str (str): temporal ranges with start and end datetimes 
        in NASA CMR-required format

    Returns:
        array: array of dictionaries with the granule hyrax urls 
    """
    
    print("Searching for granules ..")

    # orienting coordinates clockwise
    poly_epsg4326.geometry = poly_epsg4326.geometry.apply(orient, args=(1,))

    # reducing number of vertices in the polygon
    # CMR has 1000000 bytes limit
    grsm_epsg4326 = poly_epsg4326.simplify(0.0005)

    doisearch = requests.get(CMR_URL + 'collections.json?doi=' + doi).json()['feed']['entry'][0]
    concept_id = doisearch['id']
    geojson = {"shapefile": ("poly.json", poly_epsg4326.geometry.to_json(), "application/geo+json")}

    page_num = 1
    page_size = 2000 # CMR page size limit

    granule_arr = []

    while True:
        
        # defining parameters
        cmr_param = {
            "collection_concept_id": concept_id, 
            "page_size": page_size,
            "page_num": page_num,
            "temporal": temporal_str,
            "simplify-shapefile": 'true' # this is needed to bypass 5000 coordinates limit of CMR
        }
        
        granulesearch = CMR_URL + 'granules.json'
        response = requests.post(granulesearch, data=cmr_param, files=geojson)
        granules = response.json()['feed']['entry']
        
        if granules:
            for g in granules:          
                # Get Hyrax URL
                href=''
                for links in g['links']:
                    if 'title' in links and links['title'].startswith('OPeNDAP'):
                        granule_arr.append({'url':links['href']})
            page_num += 1   
        else: 
            break
        
        print(f"Total granules found: {len(granule_arr)}")
    return granule_arr   

def main():
    """Access GEDI L4A variables from Hyrax for polygon (GeoJSON file) and start/end dates, and
    saves the output as a csv file"""

    parser = parse_args(sys.argv[1:])

    doi = parser.doi
    outfile = parser.outfile
    start_date = parser.date1
    end_date = parser.date2
    beams  = parser.beams
    variables  = parser.variables
    fmt_json = parser.json
    poly = gpd.read_file(parser.poly)
    poly.crs = 'EPSG:4326'

    dt_cmr = '%Y-%m-%dT%H:%M:%SZ'
    temporal = start_date.strftime(dt_cmr) + ',' + end_date.strftime(dt_cmr)

    # setting up maximum retries to get around Hyrax 500 error
    s = requests.Session()
    retries = Retry(total=3, backoff_factor=0.1, status_forcelist=[ 500, 502, 503, 504 ])
    s.mount('https://', HTTPAdapter(max_retries=retries))

    # appending science variables to lat, lon, elev, shot_number
    for v in variables:
        if v not in HEADERS:
            HEADERS.append(v)

    # writing header row to the output file
    if not path.isfile(outfile):
        with open(outfile, "w") as f:
            f.write(','.join(HEADERS)+'\n')

    for g in get_granules_hyrax(doi, poly, temporal):
        for beam in beams:
            print(f"Downloading {g['url'].rsplit('/', 1)[-1]} / {beam}")

            # retrieving lat, lon coordinates for the file
            
            hyrax_url = f"{g['url']}.dap.nc4?dap4.ce=/{beam}/lon_lowestmode;/{beam}/lat_lowestmode"
            r = s.get(hyrax_url)
            if (r.status_code != 400):
                ds = nc.Dataset('hyrax', memory=r.content)
                lat = ds[beam]['lat_lowestmode'][:]
                lon = ds[beam]['lon_lowestmode'][:]
                ds.close()
                df = pd.DataFrame({'lat_lowestmode': lat, 'lon_lowestmode': lon}) # creating pandas dataframe  

                # subsetting by bounds of the area of interest
                # converting to geopandas dataframe
                gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lon_lowestmode, df.lat_lowestmode)) 
                gdf_sub = gdf[gdf['geometry'].within(poly.geometry[0])]   
                if not gdf_sub.empty:
                    # retrieving variables of interest, agbd, agbd_t in this case.
                    # We are only retriving the shots within subset area.
                    for _, df_gr in gdf_sub.groupby((gdf_sub.index.to_series().diff() > 1).cumsum()):
                        i = df_gr.index.min()
                        j = df_gr.index.max()
                        for v in HEADERS[2:]:
                            var_s = f"/{beam}/{v}[{i}:{j}]"
                            hyrax_url = f"{g['url']}.dap.nc4?dap4.ce={var_s}"
                            r = s.get(hyrax_url)
                            if (r.status_code != 400):
                                ds = nc.Dataset('hyrax', memory=r.content)
                                gdf_sub.loc[i:j, (v)] = ds[beam][v][:]
                                ds.close()

                    # saving the output file
                    gdf_sub['shot_number'] = gdf_sub['shot_number'].astype(str)
                    gdf_sub.to_csv(outfile, mode='a', index=False, header=False, columns=HEADERS)

    if fmt_json:
        jsonf = f"{path.splitext(outfile)[0]}.json"
        print (f"writing GeoJSON file {jsonf}")
        df = pd.read_csv(outfile)
        gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lon_lowestmode, df.lat_lowestmode))
        gdf.to_file(jsonf, driver='GeoJSON', drop_id=True)

if __name__ == "__main__":
    main()