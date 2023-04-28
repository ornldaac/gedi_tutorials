# Tutorials on GEDI Science Data Products

**Author:** ORNL DAAC       
**Date:** August 26, 2021       
**Contact for the ORNL DAAC:** uso@daac.ornl.gov

**Keywords:** lidar, GEDI, AGBD, aboveground biomass

## Overview      
These tutorials demonstrate how to discover, access, and use [GEDI science data products](https://daac.ornl.gov/gedi) archived at the ORNL DAAC. GEDI L3, L4A, and L4B data products are available in [various data tools and services](services.md).

## Prerequisites
Requirements are in [requirements.txt](requirements.txt). To install the necessary Python libraries, you can copy the [requirements.txt](requirements.txt) from this repository and run:

```bash
pip install -r requirements.txt
```

## GEDI L4A 
### Jupyter Notebooks
1. [Search and download GEDI L4A dataset](1_gedi_l4a_search_download.ipynb): search and download GEDI L4A granules over an area of interest to a local machine
1. [Subset GEDI L4A footprints](2_gedi_l4a_subsets.ipynb): subset downloaded GEDI L4A granules to an area of interest
1. [Explore GEDI L4A data structure](3_gedi_l4a_exploring_data.ipynb): explore data structure, variables, and quality flags of the GEDI L4A dataset
1. [Direct S3 Access GEDI L4A from the NASA EarthData Cloud](gedi_l4a_direct_s3_access.ipynb): retrieve the GEDI L4A dataset from NASA Earthdata Cloud using direct S3 access
1. [Access GEDI L4A dataset with NASA OPeNDAP in the Cloud](access_gedi_l4a_hyrax.ipynb): access selected variables for the GEDI L4A dataset within an area of interest using OPeNDAP Hyrax
1. [Access GEDI L4A dataset with NASA Harmony API](gedi_l4a_harmony.ipynb): direct access and subset the GEDI L4A variables using NASA Harmony API 
1. [Reproduce L4A AGBD estimates from GEDI L2A RH metrics](reconstruct_L4A_AGBD_L2A_metrics.ipynb): reconstruct L4A AGBD estimates using L2A relative height (RH) metrics
1. [Apply correction to AGBD estimates for selected L4A shots, Version 2](correct_GEDI_L4A_V002_01.ipynb): apply AGBD correction to Version 1 (V001) GEDI L4A shots affected with the algorithm setting group 10 issue

### Python Scripts
1. [Search and download GEDI L4A dataset](scripts#1-gedi_l4a_search_downloadpy): downloads GEDI L4A granules to a local directory based on GeoJSON polygon 
1. [Subset GEDI L4A footprints](scripts#2-gedi_l4a_subsetspy): subsets the downloaded GEDI L4A granules by a GeoJSON polygon file
1. [Subset GEDI L4A with NASA OPeNDAP in the Cloud](scripts#3-gedi_l4a_hyraxpy): accesses the GEDI L4A dataset using NASA's OPeNDAP Hyrax

## GEDI L4B 
### Jupyter Notebooks
1. [Access GEDI L4B Dataset with OGC Web Services](https://nbviewer.org/github/ornldaac/gedi_tutorials/blob/main/gedi_l4b_ogc.ipynb): visualize and access the GEDI L4B dataset using the OGC WMS and WCS services

## Related Resources
- NASA Earthdata Webinar: [Explore NASA GEDI Aboveground Biomass Datasets, Services, and Tools at NASA's ORNL DAAC](https://daac.ornl.gov/resources/tutorials/2022_earthdata_webinar/)
- ESA Workshop: [Synergistic Use of SAR and Lidar Data for Terrestrial Ecology Research](https://daac.ornl.gov/resources/workshops/esa-2021-workshop/)

More resources related to ORNL DAAC data and web services can be found at the [ORNL DAAC Learning](https://daac.ornl.gov/resources/learning/) page.
