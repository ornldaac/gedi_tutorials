# Python Modules
The tutorials requires additional Python modules installed in your system. These are listed on the [requirements.txt](../../requirements.txt) file within the repository. You can install the modules using `pip` as:

```bash
pip install -r requirements.txt
```

If you use `conda` environment, you can create and activate the conda environment as 

```bash
conda env create -f environment.yml
conda activate gedi_tutorials
```

The tutorials specifically uses the following python modules:
1. [`earthaccess`](https://github.com/nsidc/earthaccess): `earthaccess` is a python library to search for, and download or stream NASA Earth science data with just a few lines of code. `earthaccess` handles authentication with [NASA's Earthdata Login (EDL)](https://urs.earthdata.nasa.gov/), search using [NASA's CMR](https://cmr.earthdata.nasa.gov/search/site/docs/search/api.html) and cloud-access through [fsspec](https://github.com/fsspec/filesystem_spec).
1. [`harmony-py`](https://github.com/nasa/harmony-py): `Harmony-Py` is a Python library for integrating with [NASA's Harmony Services](https://harmony.earthdata.nasa.gov/). It provides a Python client to directly using Harmony's API and handles [NASA's Earthdata Login (EDL)](https://urs.earthdata.nasa.gov/) authentication and  integrates with the [NASA's CMR](https://cmr.earthdata.nasa.gov/search/site/docs/search/api.html) by accepting collection results as a request parameter.