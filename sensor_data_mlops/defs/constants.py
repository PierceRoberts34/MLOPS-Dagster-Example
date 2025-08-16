"""
The constants file holds filepaths and important strings for the project
"""

import dagster as dg

# Path to the data folder
IOT_DATA_FILE_PATH = "data/raw/sensor_data.csv"

PAMAP2_RAW_PATH = "data/raw/PAMAP2"

PAMAP2_STAGING_PATH = "data/staging/PAMAP2"

# Remote data
REMOTE_DATA_ROOT = dg.EnvVar('REMOTE_DATA_ROOT_ID').get_value()

# Path to the remote data
REMOTE_DATA_PATH = f'{REMOTE_DATA_ROOT}/sensor_data.csv'

# Change between rows needed to trigger a new file download
CHANGE_THRESHOLD = 5

# Path to the keyfile
GDRIVE_KEY_FILE = "keys/keyfile.json"

# Checksums
CHECKSUMS_FILE = "keys/checksum.json"

PAMAP2_ACTIVITY_LABELS = [ 
                        "Lying",
                        "Sitting",
                        "Standing",
                        "Walking",
                        "Ascending Stairs",
                        "Descending Stairs",
                        "Vacuum Cleaning",
                        "Ironing"
    ]

PARAMETERS = {
    # Show training verbose: 0,1
    "showTrainVerbose":1,

    # Learning Rate for Adam Optimizer
    "learningRate": 5e-3,

    # input window size 
    "segment_size": 128,

    # input channel count
    "num_input_channels": 6,

    # local epoch
    "localEpoch": 200,

    # Step size
    "timeStep": 16,

    # Dataset Activity Count
    "activityCount": len(PAMAP2_ACTIVITY_LABELS),


    # Hyperparameters
    "batch_size": 256,
    "projection_dim": 192,
    "filterAttentionHead": 4,
}

# Model Validation
CHECKPOINT_FILEPATH = "data/evaluation/bestValcheckpoint.weights.h5"
TRAINWEIGHTS_FILEPATH = "data/evaluation/bestTrain.weights.h5"
