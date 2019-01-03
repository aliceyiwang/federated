# Copyright 2018, The TensorFlow Federated Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Implementations of the ClientData abstract base class."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import os.path

# Dependency imports

import tensorflow as tf

from tensorflow.python.util import nest
from tensorflow_federated.python.common_libs import py_typecheck
from tensorflow_federated.python.simulation import client_data


class FilePerUserClientData(client_data.ClientData):
  """ClientData that maps a set of files (one file per user) to a dataset."""

  def __init__(self, client_ids, create_tf_dataset_fn):
    """Constructs a `ClientData` object.

    Args:
      client_ids: A list of client_id(s).
      create_tf_dataset_fn: A callable that takes a client_id and returns
        a `tf.data.Dataset` object.
    """
    py_typecheck.check_type(client_ids, list)
    if not client_ids:
      raise ValueError('`cliet_ids` must have at least one client ID')
    py_typecheck.check_callable(create_tf_dataset_fn)
    self._client_ids = client_ids
    self._create_tf_dataset_fn = create_tf_dataset_fn

    g = tf.Graph()
    with g.as_default():
      tf_dataset = self._create_tf_dataset_fn(self._client_ids[0])
      self._output_types = tf_dataset.output_types
      self._output_shapes = tf_dataset.output_shapes

  @property
  def client_ids(self):
    return self._client_ids

  def create_tf_dataset_for_client(self, client_id):

    def _assert_nested_equal(nested_x, nested_y):
      nest.assert_same_structure(nested_x, nested_y)
      flat_x = nest.flatten(nested_x)
      flat_y = nest.flatten(nested_y)
      for x, y in zip(flat_x, flat_y):
        if x != y:
          raise ValueError('{x} != {y} for client with id [{id}]'.format(
              x=x, y=y, id=client_id))

    tf_dataset = self._create_tf_dataset_fn(client_id)
    _assert_nested_equal(tf_dataset.output_types, self._output_types)
    _assert_nested_equal(tf_dataset.output_shapes, self._output_shapes)
    return tf_dataset

  @property
  def output_types(self):
    return self._output_types

  @property
  def output_shapes(self):
    return self._output_shapes

  @classmethod
  def create_from_dir(cls, path, create_tf_dataset_fn=tf.data.TFRecordDataset):
    """Builds a `tff.simulation.FilePerUserClientData`.

    Iterates over all files in `path`, using the filename as the client ID. Does
    not recursively search `path`.

    Args:
      path: A directory path to search for per-client files.
      create_tf_dataset_fn: A callable that creates a `tf.data.Datasaet` object
        for a given file in the directory specified in `path`.

    Returns:
      A `FilePerUserClientData` object.
    """
    client_ids_to_paths_dict = {
        filename: os.path.join(path, filename) for filename in os.listdir(path)
    }
    return FilePerUserClientData(
        list(client_ids_to_paths_dict.keys()),
        lambda id: create_tf_dataset_fn(client_ids_to_paths_dict[id]))