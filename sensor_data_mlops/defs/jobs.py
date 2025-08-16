"""
Jobs are the main unit of execution and monitoring in Dagster.
They allow execution of a portion of a graph of asset definitions or ops based on a schedule or an external trigger.
Jobs are the link between sensors and assets.
"""

from sensor_data_mlops.defs import assets

import dagster as dg

getfile = dg.define_asset_job("getfile", selection=["iot_data_file"])

