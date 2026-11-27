import os
import pathlib

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import tensorflow as tf
import os

from tensorflow.keras import layers
from tensorflow.keras import models
from IPython import display

# Set the seed value for experiment reproducibility.
seed = 42
tf.random.set_seed(seed)
np.random.seed(seed)

path = os.path.join(os.getcwd(), "CNN/")

commands = np.array(tf.io.gfile.listdir(str(path)))
commands = commands[(commands != 'createdatasets.py') & (commands != '.DS_Store')]
print('Commands:', commands)
    
train_ds, val_ds = tf.keras.utils.text_dataset_from_directory(
    directory=path,
    labels="inferred",
    label_mode="int",
    class_names=None,
    batch_size=32,
    max_length=None,
    shuffle=True,
    seed=None,
    validation_split=None,
    subset=None,
    follow_links=False,
    format="tf",
    verbose=True,)



label_names = np.array(train_ds.class_names)
print()
print("label names:", label_names)
print("train",train_ds)























def get_spectrogram(waveform):
  # Convert the waveform to a spectrogram via a STFT.
  spectrogram = tf.signal.stft(
      waveform, frame_length=255, frame_step=128)
  # Obtain the magnitude of the STFT.
  spectrogram = tf.abs(spectrogram)
  # Add a `channels` dimension, so that the spectrogram can be used
  # as image-like input data with convolution layers (which expect
  # shape (`batch_size`, `height`, `width`, `channels`).
  spectrogram = spectrogram[..., tf.newaxis]

  return spectrogram

def get_specto():
    x = path/'label_10/sensordata_0'
    x = tf.io.read_file(str(x))
    x, sample_rate = tf.audio.decode_wav(x, desired_channels=1, desired_samples=16000,)
    x = tf.squeeze(x, axis=-1)
    waveform = x
    x = get_spectrogram(x)
    x = x[tf.newaxis,...]

    prediction = model(x)
    x_labels = ['down', 'go', 'left', 'no', 'right', 'stop', 'up', 'yes']
    plt.bar(x_labels, tf.nn.softmax(prediction[0]))
    plt.title('No')
    plt.show()