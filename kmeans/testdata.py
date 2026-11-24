import numpy as np
import matplotlib.pyplot as plt

testdata = np.zeros((600,3))
avgpoints = np.zeros((6, 3))
wonpoints = np.zeros((6,100,4))

testdata[0:100,:] = np.array([1900,1600,1600])
testdata[100:200,:] = np.array([1300,1600,1600])
testdata[200:300,:] = np.array([1600,1900,1600])
testdata[300:400,:] = np.array([1600,1300,1600])
testdata[400:500,:] = np.array([1600,1600,1900])
testdata[500:600,:] = np.array([1600,1600,1300])
testdata += 20*np.random.randn(600, 3)

def genpoints():
    for i, p in enumerate(avgpoints):
        point = np.array([np.random.randint(1150, 2050),
                         np.random.randint(1150, 2050),
                         np.random.randint(1150, 2050)])
        avgpoints[i,:] = np.array(point)
        #print(avgpoints[i])
genpoints()

def calcdist():
    for i, p in enumerate(testdata):
        for j, o in enumerate(avgpoints):
            dist = np.power(np.exp(testdata[i] - avgpoints[j], 2))
            print(dist)

calcdist()




colors = [
    'red', 'darkred',
    'green', 'darkgreen',
    'blue', 'darkblue',
    'brown'
]

labels = [
    'X max', 'X min',
    'Y max', 'Y min',
    'Z max', 'Z min'
]

fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

for i in range(6):
    start = i * 100
    end = (i + 1) * 100

    ax.scatter(
        testdata[start:end, 0],
        testdata[start:end, 1],
        testdata[start:end, 2],
        c=colors[i],
        label=labels[i],
        s=20,
        alpha=0.7
    )
for i in range(6):
    start = i 
    end = (i + 1)

    ax.scatter(
        avgpoints[start:end, 0],
        avgpoints[start:end, 1],
        avgpoints[start:end, 2],
        c=colors[6],
        s=20,
        alpha=1
    )

ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')

ax.set_title('3D dot cloud')
ax.legend()

ax.set_box_aspect([1, 1, 1])

plt.tight_layout()
plt.show()