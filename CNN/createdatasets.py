import os
import pathlib
import glob
import numpy as np
import pandas as pd
import tensorflow as tf
import matplotlib.pyplot as plt

root = pathlib.Path("data")
paths = sorted(root.glob('*[1][0-5]/sensordata_*'))

# Label from folder name; map to 0..N-1 in case numbers aren't contiguous
raw = [int(p.parent.name.split("_")[1]) for p in paths]
classes = sorted(set(raw))
labels = [classes.index(r) for r in raw]

# Split at the file level (before building datasets) to avoid leakage
from sklearn.model_selection import train_test_split
tr_p, va_p, tr_y, va_y = train_test_split(
    [str(p) for p in paths], labels, test_size=0.2, stratify=labels, random_state=0
)


def load_csv(p):
    return pd.read_csv(p).to_numpy(np.float32)  # header=None if no header row




X_tr = np.stack([load_csv(p) for p in tr_p])  # [n_files, rows, features]
X_va = np.stack([load_csv(p) for p in va_p])
y_tr = np.array(tr_y, dtype=np.int32)
y_va = np.array(va_y, dtype=np.int32)

ds_tr = (tf.data.Dataset.from_tensor_slices((X_tr, y_tr))
         .shuffle(len(X_tr))
         .batch(32)
         .prefetch(tf.data.AUTOTUNE))
ds_va = (tf.data.Dataset.from_tensor_slices((X_va, y_va))
         .batch(32)
         .prefetch(tf.data.AUTOTUNE))  # no shuffle for validation
print(ds_tr)

n_per_class = 3
classes_present = np.unique(y_tr)

fig, axes = plt.subplots(len(classes_present), n_per_class,
                         figsize=(4 * n_per_class, 2.5 * len(classes_present)),
                         sharey=True, squeeze=False)

for r, c in enumerate(classes_present):
    idx = np.where(y_tr == c)[0][:n_per_class]
    for k, i in enumerate(idx):
        ax = axes[r, k]
        for ch in range(X_tr.shape[2]):
            ax.plot(X_tr[i][:, ch], label=f"ch {ch}")
        ax.set_title(f"label {c} | {tr_p[i].split('/')[-1]}", fontsize=8)
        ax.set_xlabel("sample")
        ax.set_ylabel("amplitude")
        ax.legend(fontsize=7)

plt.tight_layout()
plt.show()


"""
def init_testdata():
    global testdata
    ROWS_PER_FILE = 4400
    
    filelist = sorted(glob.glob('*[1][0-5]/sensordata_*')) # https://stackoverflow.com/a/3348761
    #print(filelist)
    len_filelist = len(filelist)

    testdata = np.zeros((len_filelist, ROWS_PER_FILE, 3))
    print(testdata.shape)
    for i in range(len_filelist):
        #start = ROWS_PER_FILE * i
        #end = ROWS_PER_FILE * (i+1)
        testdata[i,:,:] = np.loadtxt(filelist[i], delimiter=',', skiprows=1, usecols=(0,1,2), dtype=int)
        print(f"testdata{i}", testdata[i])
        


init_testdata()
#label_names = np.array(train_ds.class_names)
#print()
#print("label names:", label_names)
#print("train",train_ds)
"""

fs = 4400  # sample rate in Hz, set yours
ch = 0      # channel to analyze

# stft works on the last axis, so move time last: [n, ch, rows]
x = tf.transpose(X_tr, [0, 2, 1])
S = tf.abs(tf.signal.stft(x, frame_length=128, frame_step=32))  # [n, ch, frames, bins]
S_db = (20 * tf.math.log(S + 1e-6) / tf.math.log(10.0)).numpy()

n_frames = S_db.shape[2]
t_max = (128 + 32 * (n_frames - 1)) / fs  # time at the end of the last frame

fig, axes = plt.subplots(len(classes_present), n_per_class,
                         figsize=(4 * n_per_class, 2.5 * len(classes_present)),
                         sharex=True, sharey=True, squeeze=False)

for r, c in enumerate(classes_present):
    idx = np.where(y_tr == c)[0][:n_per_class]
    for k, i in enumerate(idx):
        ax = axes[r, k]
        im = ax.imshow(S_db[i, ch].T, origin="lower", aspect="auto",
                       extent=[0, t_max, 0, fs / 2])
        ax.set_title(f"label {c} | {tr_p[i].split('/')[-1]}", fontsize=8)
        ax.set_xlabel("time (s)")
        ax.set_ylabel("freq (Hz)")
        ax.label_outer()

fig.colorbar(im, ax=axes, label="power (dB)")
plt.show()

