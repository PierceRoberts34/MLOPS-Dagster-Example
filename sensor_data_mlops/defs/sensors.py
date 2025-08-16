"""
Sensors take action in response to events that occur either internally within Dagster or in external systems.
They check for events at regular intervals and either perform an action or provide an explanation for why the action was skipped.
"""

import json

from sensor_data_mlops.defs import constants
from sensor_data_mlops.defs import jobs
from sensor_data_mlops.defs.utils import save_data_to_json
from sensor_data_mlops.defs.filestorebucket import FileStoreBucket

import dagster as dg

# Define the sensor to check whether the file has been updated
@dg.sensor(
    job=jobs.getfile,
    minimum_interval_seconds=30, # Define how frequently the sensor should poll for changes
    default_status=dg.DefaultSensorStatus.RUNNING,  # Sensor is turned on by default
)
def file_change_sensor(fsb: FileStoreBucket):
    fs = fsb.create_fs()
    remote_checksum = fs.info(constants.REMOTE_DATA_PATH)['checksum'] # Use fsspec's info property to get the checksum of the file in remote storage
    # Try to load the checksum of the last time a check was performed.
    try:
      with open(constants.CHECKSUMS_FILE, 'r') as file:
        js = json.load(file)
        local_checksum = js['checksum']
    except:
      local_checksum = ''
    if (local_checksum != remote_checksum):
      save_data_to_json(constants.CHECKSUMS_FILE, 'checksum', remote_checksum)
      yield dg.RunRequest(run_key=remote_checksum) # Run a job using the checksum as the run key, in case another job is called while the previous job is running.
    else:
      yield dg.SkipReason("No file changes") # If the checksums match, the file hasn't changed and no further action is needed.


