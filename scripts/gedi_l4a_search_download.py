#!/usr/bin/env python3

import argparse
import http.cookiejar
import pathlib
import requests
import hashlib
import sys
import datetime as dt
import geopandas as gpd
from os import path
from shapely.ops import orient
from urllib.parse import urlsplit

# CMR API base url
CMR_URL="https://cmr.earthdata.nasa.gov/search/"
AUTH_HOST = "https://urs.earthdata.nasa.gov"
EDL_AUTH = "https://wiki.earthdata.nasa.gov/display/EL/How+To+Access+Data+With+cURL+And+Wget"
DT_FORMAT = "%Y-%m-%d"
GRANULE_FORMAT = "h5"

def parse_args(args):
    """Parses command line agruments."""

    parser = argparse.ArgumentParser(
        description="Search and Download GEDI L4A Granules",
        usage="gedi_l4a_search_download.py --doi <DOI> --date1 <start_date> --date2 <end_date> --poly <path_to_geojson_file> --outdir <path_to_directory>\n"
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
        "--outdir",
        required=True, 
        type=pathlib.Path, 
        help="path to the directory for saving downloaded files"
    )

    return parser.parse_args(args)


class EDLSession(requests.Session):
    """Creates a NASA EarthData Login session. More info at https://urs.earthdata.nasa.gov/documentation/what_do_i_need_to_know
    From https://github.com/asfadmin/Discovery-asf_search/
    """
    def __init__(self):
        super().__init__()

    def auth_with_creds(self, username: str, password: str):
        self.auth = (username, password)
        self.get(AUTH_HOST)
        if "urs_user_already_logged" not in self.cookies.get_dict():
            raise Exception("Username or password is incorrect")
        return self

    def auth_with_token(self, token: str):
        self.headers.update({'Authorization': 'Bearer {0}'.format(token)})
        return self

    def auth_with_cookiejar(self, cookies: http.cookiejar):
        self.cookies = cookies
        return self
       
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

def check_sha256(granule_url: str, local_file: str):
    """Checks if date parameters are in correct format.

    Args:
        granule_url (str): download url of granule
        local_file (str): full path of local file
    
    Returns:
        bool: whether the sha256 hashes of local and remote file 
        are same
    """
    response = requests.get(granule_url)
    response.raise_for_status()
    sha256_1 = response.content.decode("utf-8")
    sha256_2 = hashlib.sha256()
    with open(local_file,'rb') as f:
        while True: 
            data = f.read(4096)
            if len(data) == 0:
                break
            else:
                sha256_2.update(data)
    return sha256_1 == sha256_2.hexdigest()


def download_files(local_file: str, session, **granule):
    """Downloads the granules.
    
    Args:
        granule (dict): granule url and sha256 
        local_file (str): full path of local file
    """

    if session is None:
        session = EDLSession()
    
    if path.isfile(local_file) and granule['sha256'] and check_sha256(granule['sha256'], local_file):
        print(f'{path.basename(local_file)} is already downloaded at {path.dirname(local_file)}')
    else:
        print(f'Downloading {path.basename(local_file)} ...')
         # Large file download https://stackoverflow.com/questions/16694907/download-large-file-in-python-with-requests
        try:
            with session.get(granule['url'], stream=True) as r:
                r.raise_for_status()
                with open(local_file, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192): 
                        f.write(chunk)
        except requests.exceptions.HTTPError as e:
            raise Exception(f"{e.response}.\r\n Set up NASA Earthdata Login authentication at {EDL_AUTH}")


def get_granules_names(doi: str, poly_epsg4326, temporal_str: str):
    """Get url and sha256 of granules that overlaps the temporal and 
    spatial bounds.
    
    Args:
        doi (str): dataset DOI
        poly_epsg4326: GeoDataFrame object containing the polygon object
        temporal_str (str): temporal ranges with start and end datetimes 
        in NASA CMR-required format

    Returns:
        array: array of dictionaries with the granule urls and sha256 hashes 
    """
    
    print("Searching for granules ..")

    # orienting coordinates clockwise
    poly_epsg4326.geometry = poly_epsg4326.geometry.apply(orient, args=(1,))

    # reducing number of vertices in the polygon
    # CMR has 1000000 bytes limit
    grsm_epsg4326 = poly_epsg4326.simplify(0.0005)

    doisearch = requests.get(CMR_URL + 'collections.json?doi=' + doi).json()['feed']['entry'][0]
    concept_id = doisearch['id']
    data_center = doisearch['data_center']
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
                # Get URL of HDF5 files
                href=''
                sha256 =''
                for links in g['links']:
                    if 'href' in links:
                        if not data_center.startswith('ORNL'): 
                            if links['href'].endswith(GRANULE_FORMAT):
                                href = links['href']
                        else:
                            if links['href'].endswith(GRANULE_FORMAT) and links['title'].startswith('Download'):
                                href = links['href']
                            if links['href'].endswith('.sha256'):
                                sha256 = links['href']
                                
                granule_arr.append({'url':href, 'sha256':sha256})
            page_num += 1   
        else: 
            break
        
        print(f"Total granules found: {len(granule_arr)}")
    return granule_arr

def main():
    parser = parse_args(sys.argv[1:])

    doi = parser.doi

    outdir = parser.outdir

    start_date = parser.date1
    end_date = parser.date2

    dt_cmr = '%Y-%m-%dT%H:%M:%SZ'
    temporal = start_date.strftime(dt_cmr) + ',' + end_date.strftime(dt_cmr)
    
    poly = gpd.read_file(parser.poly)
    poly.crs = 'EPSG:4326'

    session = EDLSession()

    for g in get_granules_names(doi, poly, temporal):
        download_files(path.join(outdir, g['url'].rsplit('/', 1)[1]), session, **g)

if __name__ == "__main__":
    main()