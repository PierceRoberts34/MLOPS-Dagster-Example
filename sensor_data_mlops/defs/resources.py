"""
Classes which are used for database and storage bucket connections should be added to dagster definitions here
"""

from sensor_data_mlops.defs.filestorebucket import FileStoreBucket

import dagster as dg

@dg.definitions
def defs() -> dg.Definitions:
    return dg.Definitions(
        resources={
            "fsb": FileStoreBucket(name="foo"),
            },
    )

