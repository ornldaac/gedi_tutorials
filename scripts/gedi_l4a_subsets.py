#!/usr/bin/env python3
import argparse
import h5py
import pathlib
import sys
import geopandas as gpd
import numpy as np
import pandas as pd
from glob import glob
from os import path, remove

GRANULE_FORMAT = "h5"

def parse_args(args):
    """Parses command line agruments."""

    parser = argparse.ArgumentParser(
        description="Subset GEDI L4A footprints",
        usage="gedi_l4a_subsets.py --poly <path_to_geojson_file> --indir <path_to_input_directory> --subdir <path_to_output_directory> [--csv] [--json]\n"
    )
    parser.add_argument(
        "--poly",
        required=True, 
        type=argparse.FileType('r', encoding='UTF-8'), 
        help="path to a GeoJSON file defining area of interest"
    )
    parser.add_argument(
        "--indir",
        required=True, 
        type=pathlib.Path, 
        help="path to the directory with downloaded h5 files"
    )
    parser.add_argument(
        "--subdir",
        required=True, 
        type=pathlib.Path, 
        help="path to the directory for saving subset files"
    )
    parser.add_argument(
        "--csv",
        default=False,
        action='store_true',
        help="setting this creates additional output CSV subset file"
    )
    parser.add_argument(
        "--json",
        default=False,
        action='store_true',
        help="setting this creates additional output GeoJSON subset file"
    )

    return parser.parse_args(args)

def create_csv_json(outdir: str, fmt_json: bool, fmt_csv: bool):
    """Creates subset data in CSV and GeoJSON formats if the 
    arguments --csv and/or --json are set.

    Args:
        outdir (str): directory path of subset h5 files
        fmt_json (bool): GeoJSON output requested
        fmt_csv (bool): CSV output requested
    """
    subset_df = pd.DataFrame()
    for subfile in glob(path.join(outdir, '*.h5')):
        hf_in = h5py.File(subfile, 'r')
        for v in list(hf_in.keys()):
            if v.startswith('BEAM'):
                col_names = []
                col_val = []
                beam = hf_in[v]
                # copy BEAMS 
                for key, value in beam.items():
                    # looping through subgroups
                    if isinstance(value, h5py.Group):
                        for key2, value2 in value.items():
                            if (key2 != "shot_number"):
                                # xvar variables have 2D
                                if (key2.startswith('xvar')):
                                    for r in range(4):
                                        col_names.append(key2 + '_' + str(r+1))
                                        col_val.append(value2[:, r].tolist())
                                else:
                                    col_names.append(key2)
                                    col_val.append(value2[:].tolist())
                    
                    #looping through base group
                    else:
                        # xvar variables have 2D
                        if (key.startswith('xvar')):
                            for r in range(4):
                                col_names.append(key + '_' + str(r+1))
                                col_val.append(value[:, r].tolist())
                        else:
                            col_names.append(key)
                            col_val.append(value[:].tolist())
                
                # create a pandas dataframe        
                beam_df = pd.DataFrame(map(list, zip(*col_val)), columns=col_names) 
                # Inserting BEAM names
                beam_df.insert(0, 'BEAM', np.repeat(str(v), len(beam_df.index)).tolist())
                beam_df.insert(0, 'filename', np.repeat(path.basename(subfile), len(beam_df.index)).tolist() )
                # Appending to the subset_df dataframe
                subset_df = pd.concat([subset_df, beam_df])
        hf_in.close()

    if not subset_df.empty:
         # convert object types columns to strings. object types are not supported
        for c in subset_df.columns:
            if subset_df[c].dtype == 'object':
                subset_df[c] = subset_df[c].astype(str)

        if fmt_csv:
            subset_df.to_csv(path.join(outdir, 'subset.csv'), index=False)
        
        # Export to GeoJSON
        if fmt_json:
            subset_gdf = gpd.GeoDataFrame(subset_df, geometry=gpd.points_from_xy(subset_df.lon_lowestmode, subset_df.lat_lowestmode))
            subset_gdf.to_file(path.join(outdir, 'subset.json'), driver='GeoJSON', drop_id=True)

def main():
    """Subsets h5 files at the indir based on the polygon (GeoJSON file) and 
    saves  as h5 files at the outdir"""

    parser = parse_args(sys.argv[1:])

    fmt_csv = parser.csv
    fmt_json = parser.json
    indir = parser.indir
    outdir = parser.subdir

    poly = gpd.read_file(parser.poly)
    poly.crs = 'EPSG:4326'

    for g in sorted(glob(path.join(indir, '*.' + GRANULE_FORMAT))):
        print(g)
        name, ext = path.splitext(path.basename(g))
        subfilename = "{name}_sub{ext}".format(name=name, ext=ext)
        outfile = path.join(outdir, subfilename)
        hf_in = h5py.File(g, 'r')
        hf_out = h5py.File(outfile, 'w')

         # loop through BEAMXXXX groups
        for v in list(hf_in.keys()):
            if v.startswith('BEAM'):
                beam = hf_in[v]
                # find the shots that overlays the area of interest
                lat = beam['lat_lowestmode'][:]
                lon = beam['lon_lowestmode'][:]
                i = np.arange(0, len(lat), 1) # index
                l4adf = pd.DataFrame(list(zip(lat,lon, i)), columns=["lat_lowestmode", "lon_lowestmode", "i"])
                l4agdf = gpd.GeoDataFrame(l4adf, geometry=gpd.points_from_xy(l4adf.lon_lowestmode, l4adf.lat_lowestmode))
                l4agdf.crs = "EPSG:4326"
                indices = l4agdf[l4agdf['geometry'].within(poly.geometry[0])].i

                # copy BEAMS to the output file
                if (len(indices) > 0):
                    for key, value in beam.items():
                        if isinstance(value, h5py.Group):
                            for key2, value2 in value.items():
                                group_path = value2.parent.name
                                group_id = hf_out.require_group(group_path)
                                dataset_path = group_path + '/' + key2
                                hf_out.create_dataset(dataset_path, data=value2[:][indices])
                                for attr in value2.attrs.keys():
                                    hf_out[dataset_path].attrs[attr] = value2.attrs[attr]
                        else:
                            group_path = value.parent.name
                            group_id = hf_out.require_group(group_path)
                            dataset_path = group_path + '/' + key
                            hf_out.create_dataset(dataset_path, data=value[:][indices])
                            for attr in value.attrs.keys():
                                hf_out[dataset_path].attrs[attr] = value.attrs[attr]

        if (len(hf_out.keys()) > 0):
            # copy ANCILLARY and METADATA groups
            for v in ["/ANCILLARY", "/METADATA"]:
                hf_in.copy(hf_in[v],hf_out)
            hf_out.close()
        else:
            hf_out.close()
            # delete file with no BEAMS
            remove(outfile)
        
        hf_in.close()

    if fmt_csv or fmt_json:
        create_csv_json(outdir, fmt_json, fmt_csv)


if __name__ == "__main__":
    main()