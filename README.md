# MLOps
Machine Learning Operations (ML + DevOps)

The purpose of this repository is to provide users with an MLOps pipeline demo using open source software.

# Getting Started
## Enabling Google Drive API
Using the [Google Drive API](https://developers.google.com/workspace/drive/api/guides/about-sdk), create a Google Cloud project with Drive API enabled and add a service account. Save the "keyfile.json" and add it to the `keys` directory

## Configuring the instance

Configure the `dagster.yaml` files to add appropriate paths for the `keys` and `data` folders. Edit the `.env` file to set the root of your cloud storage.

# Usage
## Docker (Recommended)
Run the provided docker compose file. The default dagster webserver port is located at `localhost:3000`. The dagster webserver allows the user to monitor runs and asset materialization.
## Local
Install uv. Run the command `uv` sync in the project directory, enter the virtual environment, and run `dagster dev`. Local development is primarily useful for testing rather than production.

# Operation
A generator for creating synthetic data within Google Drive is included in the TimeGan folder. This notebook is meant to be run in Google Colab.

The main project includes a dagster sensor which looks for changes in the Google cloud drive using the fsspec info property to get hash changes. If a change is detected, then an asset is run which checks for the number of rows present in the new file which are not present in the existing data. Once the number of different rows in the cloud data passes the threshold number defined in the `constants.py` file, then the asset downloads the file from cloud storage and marks the asset as materialized.
