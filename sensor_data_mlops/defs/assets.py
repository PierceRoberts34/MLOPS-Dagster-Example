"""
An asset is an object in persistent storage, such as a table, file, or persisted machine learning model. 
An asset definition is a description, in code, of an asset that should exist and how to produce and update that asset.
The assets.py file contains all assets used in the project
"""

import numpy as np
import os
import pandas as pd
import requests
import time
import zipfile

# Machine Learning Modules
import tensorflow as tf
from tensorflow import keras
from sklearn.utils import class_weight
# Project Files
from dagster._utils.backoff import backoff
from sensor_data_mlops.defs import constants
from sensor_data_mlops.defs.filestorebucket import FileStoreBucket
from sensor_data_mlops.defs import model
from sensor_data_mlops.defs import utils
import dagster as dg

# Define the external asset
raw_iot_data = dg.AssetSpec("raw_iot_data")

@dg.asset()
def checksums_file(): 
    """
    Checksums file to download data
    """

# Download external asset from fsspec remote storage
@dg.asset(
      deps=["raw_iot_data"],
      output_required=False
)
def iot_data_file(fsb: FileStoreBucket):
  """
  Raw data downloaded from external storage
  """
  fs = fsb.create_fs()

  # Function to download IOT file
  def download_iot_file():
    fs.get(constants.REMOTE_DATA_PATH, constants.IOT_DATA_FILE_PATH)
  # We want to open both the remote and local copy of the dataset for comparison
  of = fs.open(constants.REMOTE_DATA_PATH,  mode='rt', cache_storage='/tmp/cache1')
  try:
    with of as file1, open(constants.IOT_DATA_FILE_PATH, "r") as file2:
      f1_contents = file1.readlines()
      f2_contents = file2.readlines()
  except:
      # If no local file is present, we download from storage.
      download_iot_file()
      return dg.MaterializeResult("Missing local file, Starting file download")
  rows_added = 0 # Represents the number of new rows in the data stored in cloud storage
  for line in f1_contents:
    if line not in f2_contents:
      rows_added += 1
  print(rows_added)
  # Download if enough new rows are added
  if (rows_added > constants.CHANGE_THRESHOLD):
    print("Starting download of new file")
    download_iot_file()
    yield dg.MaterializeResult()
  else:
    print("Not enough new data, skipping download")


@dg.asset
def pamap2_raw() -> None:
    """
    The raw data files for the PAMAP2 Dataset, downloaded from UC Irvine.
    """

    raw_pamap2_dset = requests.get(
        "http://archive.ics.uci.edu/ml/machine-learning-databases/00231/PAMAP2_Dataset.zip"
    )

    # Save dataset to raw data directory
    archive = f'{constants.PAMAP2_RAW_PATH}.zip'
    with open(archive, "wb") as output_file:
        output_file.write(raw_pamap2_dset.content)

    # The dataset must be extracted before use
    with zipfile.ZipFile(archive, 'r') as zip_ref:
      zip_ref.extractall(constants.PAMAP2_RAW_PATH)

    # The archive is no longer needed now that it has been extracted
    os.remove(archive)

@dg.asset(deps=["pamap2_raw"])
def pamap2_numpy():
  """
  The dataset exported to numpy arrays for easy import
  """
  data_dir =f'{constants.PAMAP2_RAW_PATH}/PAMAP2_Dataset/Protocol'
  np_dir = constants.PAMAP2_STAGING_PATH 
  print("\n#####Preprocessing PAMAP2#####\n")
  if not os.path.isdir(np_dir):
      os.makedirs(np_dir)

  for filename in os.listdir(data_dir):
      print(filename)
      inpath = os.path.join(data_dir,filename)
      outpath = os.path.join(np_dir,filename.split('.')[0])
      utils.convert(inpath, outpath)

@dg.multi_asset(
  deps=["pamap2_numpy"],
  outs={"training_data": dg.AssetOut(), "validation_data": dg.AssetOut(), "test_data": dg.AssetOut(), "class_weights": dg.AssetOut()}
)
def create_train_val_test():
  """
  The Train, Validation, and Test Datasets for the model
  """
  params = constants.PARAMETERS
  TrainData, TrainLabel = utils.get_dataset_from_files([101, 102, 103, 104, 105, 106], params["segment_size"], params["timeStep"])
  DevData, DevLabel = utils.get_dataset_from_files([107], params["segment_size"], params["timeStep"])
  TestData, TestLabel = utils.get_dataset_from_files([108], params["segment_size"], params["timeStep"])
  class_weights = utils.get_class_weights(TrainLabel)

  # Encode data for the model
  TrainLabel, DevLabel, TestLabel = utils.encode_labels(TrainLabel, DevLabel, TestLabel)
  
  return (TrainData, TrainLabel), (DevData, DevLabel), (TestData, TestLabel), class_weights


@dg.asset(deps=["training_data","validation_data",  "test_data", "class_weights"])
def trainModel(training_data, validation_data, test_data, class_weights):

  # Initialize needed components
  TrainData, TrainLabel = training_data
  DevData, DevLabel = validation_data
  TestData, TestLabel = test_data, 
  class_weights = class_weights
  learningRate = constants.PARAMETERS["learningRate"]
  segment_size = constants.PARAMETERS["segment_size"]
  num_input_channels = constants.PARAMETERS["num_input_channels"]
  activityCount = constants.PARAMETERS["activityCount"]
  batch_size = constants.PARAMETERS["batch_size"]
  localEpoch = constants.PARAMETERS["localEpoch"]
  showTrainVerbose = constants.PARAMETERS["showTrainVerbose"]

  optimizer = tf.keras.optimizers.Adam(learningRate)
  input_shape = (segment_size, num_input_channels)
  model_classifier = model.HART(input_shape, activityCount)

  model_classifier.compile(
      optimizer=optimizer,
      loss=tf.keras.losses.CategoricalCrossentropy(label_smoothing=0.1),
      metrics=["accuracy"],
  )
  model_classifier.summary()

  # Save best model validation weights
  checkpoint_filepath = constants.CHECKPOINT_FILEPATH
  checkpoint_callback = tf.keras.callbacks.ModelCheckpoint(
      checkpoint_filepath,
      monitor="val_accuracy",
      save_best_only=True,
      save_weights_only=True,
      verbose=1,
  )

  start_time = time.time()
  history = model_classifier.fit(
      x=TrainData,
      y=TrainLabel,
      validation_data = (DevData,DevLabel),
      batch_size=batch_size,
      epochs=localEpoch,
      verbose=showTrainVerbose,
      class_weight=class_weights,
      callbacks=[checkpoint_callback],
  )
  end_time = time.time() - start_time

  model_classifier.save_weights(constants.TRAINWEIGHTS_FILEPATH)
  model_classifier.load_weights(constants.CHECKPOINT_FILEPATH)
  _, accuracy = model_classifier.evaluate(TestData, TestLabel)
  print(f"Test accuracy: {round(accuracy * 100, 2)}%")
  yield dg.MaterializeResult(f"Test accuracy: {round(accuracy * 100, 2)}%")








