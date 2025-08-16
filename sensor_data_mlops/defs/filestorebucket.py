"""
Class used for Google Drive integration.
"""

from pydrive2.fs import GDriveFileSystem
from sensor_data_mlops.defs import constants

import dagster as dg

class FileStoreBucket(dg.ConfigurableResource):
    def create_fs(self):
        fs = GDriveFileSystem(
            constants.REMOTE_DATA_ROOT,
            use_service_account=True,
            client_json_file_path=constants.GDRIVE_KEY_FILE
        )
        return fs

