# Python scripts

## 1. gedi_l4a_search_download.py

This script downloads GEDI L4A granules.

### usage
```
./gedi_l4a_search_download.py --doi <DOI> --date1 <start_date> --date2 <end_date> --poly <path_to_geojson_file> --outdir <path_to_directory>
```
### arguments
| argument  | description |
| ------------- | ------------- |
| --help  |  show help message and exit  |
| --doi | dataset DOI e.g., 10.3334/ORNLDAAC/2056 for GEDI L4A V2.1 |
| --date1 | start date in YYYY-MM-DD format |
| --date2 | start date in YYYY-MM-DD format |
| --poly | path to a GeoJSON file defining area of interest|
| --outdir | path to the directory for saving downloaded h5 files |

### example usage

```
./gedi_l4a_search_download.py --date1 2019-12-15 --date2 2020-01-12 --doi 10.3334/ORNLDAAC/2056 --poly ../polygons/amapa.json --outdir ../full_orbits/
```

## 2. gedi_l4a_subsets.py

This script subsets GEDI L4A footprints by geojson.

### usage
```
./gedi_l4a_subsets.py --poly <path_to_geojson_file> --indir <path_to_input_directory> --subdir <path_to_output_directory> [--csv] [--json]
```
### arguments
| argument  | description |
| ------------- | ------------- |
| --help  |  show help message and exit  |
| --poly | path to a GeoJSON file defining area of interest|
| --indir | path to the directory with downloaded h5 files |
| --subdir | path to the directory for saving subset files |
| --csv | (optional) setting this creates additional output CSV subset file |
| --json | (optional) setting this creates additional output GeoJSON subset file |

### example usage

```
./gedi_l4a_subsets.py --poly ../polygons/amapa.json --indir ../full_orbits/ --subdir ../subsets/ --csv
```
