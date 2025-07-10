import json
import numpy as np
import pandas as pd
# from tensorflow import keras
# from keras import layers
from dagster._utils.backoff import backoff
from sensor_data_mlops.defs import constants
from pydrive2.fs import GDriveFileSystem

import dagster as dg

fs = GDriveFileSystem(
constants.REMOTE_DATA_ROOT,
use_service_account=True,
client_json_file_path=constants.GDRIVE_KEY_FILE
)

# Function to save checksum to json file
def save_checksum_to_json(file_path, checksum):
    data = {"checksum": checksum}
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)

def download_iot_file():
   print("Starting download of new data file")
   fs.get(constants.REMOTE_DATA_PATH, constants.IOT_DATA_FILE_PATH)

# Define the external asset
raw_iot_data = dg.AssetSpec("raw_iot_data")

# Download external asset from fsspec remote storage
@dg.asset(
      deps=["raw_iot_data"]
)
def iot_data_file() -> None:
    # Get the last copy of the data
    try:
       with open(constants.IOT_DATA_FILE_PATH) as f:
        oldrow = pd.read_csv(f,usecols=['X','Y','Z']).tail(1)
    except:
      download_iot_file()
    # Check remote data for changes
    with fs.open(constants.REMOTE_DATA_PATH) as f:
       newrow = pd.read_csv(f,usecols=['X','Y','Z']).tail(1)
    distance = np.linalg.norm(newrow - oldrow) # We use the Euclidan Normal to check for significant changes.
    if (distance > constants.CHANGE_THRESHOLD): # The threshold value can be changed with the constants value
       download_iot_file()

@dg.asset(
   deps=["iot_data_file"]
)
def prepared_iot_data() -> None:
  with open(constants.IOT_DATA_FILE_PATH) as f:
    df = pd.read_csv(f)
  df = df.dropna()
  df['eNorm'] = np.linalg.norm(df[['X', 'Y', 'Z']], axis=1)


# Job to download external asset
getfile = dg.define_asset_job("getfile", selection=["iot_data_file"])

# Define the sensor to check whether the file is updated
@dg.sensor(
    job=getfile,
    minimum_interval_seconds=5,
    default_status=dg.DefaultSensorStatus.RUNNING,  # Sensor is turned on by default
)
def file_change_sensor():
    with open(constants.CHECKSUMS_FILE, 'r') as file:
      js = json.load(file)
      local_checksum = js['checksum']
    remote_checksum = fs.info(constants.REMOTE_DATA_PATH)['checksum']
    if (local_checksum != remote_checksum):
      save_checksum_to_json(constants.CHECKSUMS_FILE, remote_checksum)
      yield dg.RunRequest(run_key=remote_checksum)
    else:
      yield dg.SkipReason("No file changes")

  
