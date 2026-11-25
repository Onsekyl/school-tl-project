import numpy as np



sensordata = np.loadtxt('sensordata_0.csv', delimiter=',', skiprows=1, dtype=int)
print(sensordata)
print(sensordata.shape)