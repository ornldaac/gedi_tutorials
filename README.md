# GEDI Science Data Tutorials

## Overview      
These tutorials demonstrate how to discover, access, and use [GEDI science data products](docs/datasets.md) archived at the ORNL DAAC. GEDI L3, L4A, L4B, and L4C data products are available in [various data tools and services](docs/services.md).

## GEDI L4A Footprint Level Aboveground Biomass Density
### Jupyter Notebooks 
1. [Search and download GEDI L4A dataset](notebooks/gedi_l4a_search_download.ipynb): search and download GEDI L4A granules over an area of interest to a local machine
1. [Subset GEDI L4A footprints](notebooks/gedi_l4a_subsets.ipynb): subset downloaded GEDI L4A granules to an area of interest
1. [Explore GEDI L4A data structure](notebooks/gedi_l4a_exploring_data.ipynb): explore data structure, variables, and quality flags of the GEDI L4A dataset. 
1. [Direct S3 Access GEDI L4A from the NASA EarthData Cloud](notebooks/gedi_l4a_direct_s3_access.ipynb): retrieve the GEDI L4A dataset from NASA Earthdata Cloud using direct S3 access. [![Open in SageMaker Studio Lab](https://studiolab.sagemaker.aws/studiolab.svg)](https://studiolab.sagemaker.aws/import/github/ornldaac/gedi_tutorials/blob/main/gedi_l4a_direct_s3_access.ipynb)
1. [Access GEDI L4A dataset with NASA OPeNDAP in the Cloud](notebooks/gedi_l4a_access_hyrax.ipynb): access selected variables for the GEDI L4A dataset within an area of interest using OPeNDAP Hyrax 
1. [Access GEDI L4A dataset with NASA Harmony API](notebooks/gedi_l4a_harmony.ipynb): direct access and subset the GEDI L4A variables using NASA Harmony API 
1. [Reproduce L4A AGBD estimates from GEDI L2A RH metrics](notebooks/gedi_reconstruct_AGBD_L2A_metrics.ipynb): reconstruct L4A AGBD estimates using L2A relative height (RH) metrics
1. [Apply correction to AGBD estimates for selected L4A shots, Version 2](notebooks/gedi_l4a_correct_V002_01.ipynb): apply AGBD correction to Version 1 (V001) GEDI L4A shots affected with the algorithm setting group 10 issue
1. [On-Cloud Data Retrieval and Analysis: Aboveground biomass from GEDI, ICESat-2 and Field Data](notebooks/gedi_icesat2_field_cloud.ipynb): directly access and retrieve the GEDI dataset, ICESat-2 and Field Data in the cloud

### Python Scripts
1. [Search and download GEDI L4A dataset](scripts/gedi_l4a_search_download.py): downloads GEDI L4A granules to a local directory based on GeoJSON polygon 
1. [Subset GEDI L4A footprints](scripts/gedi_l4a_subsets.py): subsets the downloaded GEDI L4A granules by a GeoJSON polygon file
1. [Subset GEDI L4A with NASA OPeNDAP in the Cloud](scripts/gedi_l4a_hyrax.py): accesses the GEDI L4A dataset using NASA's OPeNDAP Hyrax

## GEDI L4B Gridded Aboveground Biomass Density
### Jupyter Notebooks
1. [Access GEDI L4B Dataset with OGC Web Services](notebooks/gedi_l4b_ogc.ipynb): visualize and access the GEDI L4B dataset using the OGC WMS and WCS services

```{include} citation.md
```