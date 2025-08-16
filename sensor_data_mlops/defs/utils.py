"""
If a function cannot be categorized under one of the dagster definitions, it should be contained here. 
"""

import json
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.utils import class_weight
from scipy.stats import mode
import tensorflow as tf

from sensor_data_mlops.defs import constants

# Function to save checksum to json file
def save_data_to_json(file_path, key, value):
  try:
    with open(file_path, 'r') as file:
      js = json.load(file)
  except:
    js = {}
  js.update({key: value})
  with open(file_path, 'w') as json_file:
      json.dump(js, json_file, indent=4)


# Create an array by loading txt file, the format used by the PAMAP dataset
def array_from_txt(inpath):
    with open(inpath) as f:
        d = f.readlines()
        array = np.array([[float(x) for x in line.split()] for line in d])
    return array

# Convert arrays to npy files.
def convert(inpath,outpath):
    array = array_from_txt(inpath)

    # Timestamps are in the first column
    timestamps = array[:,0]

    # The activity labels are located in the second column
    labels = array[:,1].astype(int)

    # We include 3 columns representing accelerometer readings and 3 columns representing gyroscope readings
    array = array[:, [4,5,6,10,11,12]]
    
    # Save dataset to file for easy loading
    np.save(outpath+'_timestamps',timestamps)
    np.save(outpath+'_labels',labels)
    np.save(outpath,array)


# Function to create datasets from npy files
def get_dataset_from_files(subj_ids, time_steps, step):
  data = np.concatenate([np.load(f'{constants.PAMAP2_STAGING_PATH}/subject{s}.npy') for s in subj_ids])
  labels = np.concatenate([np.load(f'{constants.PAMAP2_STAGING_PATH}/subject{s}_labels.npy') for s in subj_ids])
  
  # Keep the 8 activities common to all subjects
  data = data[np.isin(labels, [1, 2, 3, 4, 12, 13, 16, 17])]
  labels = labels[np.isin(labels, [1, 2, 3, 4, 12, 13, 16, 17])]

  # Remove Missing Values
  data_nans = np.isnan(data).any(axis=1)
  data = data[~data_nans]
  labels = labels[~data_nans]

  # Standardize the data
  scaler = StandardScaler()
  scaler.fit(data)
  data = scaler.transform(data)

  # Reshape the data
  segments = []
  segment_labels = []

  n_samples, n_features = data.shape
  for i in range(0, n_samples - time_steps, step):
      segment = data[i:i + time_steps, :]  # all features in the window
      label = mode(labels[i:i + time_steps], keepdims=True)[0][0]  # most frequent label
      segments.append(segment)
      segment_labels.append(label)

  data = np.array(segments, dtype=np.float32)
  labels = np.array(segment_labels)
  return data, labels

def get_class_weights(TrainLabel):
  temp_weights = class_weight.compute_class_weight(class_weight = 'balanced',
                                                  classes = np.unique(TrainLabel),
                                                  y = TrainLabel.ravel())
  class_weights = {j : temp_weights[j] for j in range(len(temp_weights))}
  return class_weights

# Prepare labels using One Hot Encoding
def onehot_encode_labels(label):
  activityCount = constants.PARAMETERS["activityCount"]
  label = tf.one_hot(
    label,
    activityCount,
    on_value=None,
    off_value=None,
    axis=None,
    dtype=None,
    name=None
  )
  return label

# Perform all encoding steps on train, validation, and test labels
def encode_labels(train_labels, val_labels, test_labels):
    found_labels = []
    index = 0
    mapping = {}
    for i in train_labels:
        if i in found_labels:
            continue
        mapping[i] = index
        index += 1
        found_labels.append(i)
    
    # Apply mapping to train, test, validation
    encoded_train_labels = [mapping[i] for i in train_labels]
    encoded_val_labels = [mapping[i] for i in val_labels]
    encoded_test_labels = [mapping[i] for i in test_labels]

    # Apply onehot encoding to train, test, validation
    encoded_train_labels = onehot_encode_labels(encoded_train_labels)
    encoded_val_labels = onehot_encode_labels(encoded_val_labels)
    encoded_test_labels = onehot_encode_labels(encoded_test_labels)

    return encoded_train_labels, encoded_val_labels , encoded_test_labels 

