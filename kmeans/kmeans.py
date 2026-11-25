import numpy as np
import matplotlib.pyplot as plt

# https://stackoverflow.com/a/2891805
np.set_printoptions(precision = 2) # Limits the decimals to the value
np.set_printoptions(suppress=True) # Disables scientific notation



testdata  = np.zeros((600, 3))
avgpoints = np.zeros((6, 3))
wonpoints_cumul = np.zeros((6, len(testdata), 4)) # 4 -> x, y, z, count

# Hardcoded testdata and avgpoints for testing:
# testdata 0-99 -> avgpoint 0, testdata 100-199 -> avgpoint 1 etc.
# testdata[0:100,:]   = np.array((1900,1600,1600))
# testdata[100:200,:] = np.array((1300,1600,1600))
# testdata[200:300,:] = np.array((1600,1900,1600))
# testdata[300:400,:] = np.array((1600,1300,1600))
# testdata[400:500,:] = np.array((1600,1600,1900))
# testdata[500:600,:] = np.array((1600,1600,1300))
# testdata += 20*np.random.randn(600, 3)

# avgpoints[0,:] = np.array((1900,1600,1600))
# avgpoints[1,:] = np.array((1300,1600,1600))
# avgpoints[2,:] = np.array((1600,1900,1600))
# avgpoints[3,:] = np.array((1600,1300,1600))
# avgpoints[4,:] = np.array((1600,1600,1900))
# avgpoints[5,:] = np.array((1600,1600,1300))
# avgpoints += 50*np.random.randn(6, 3)

def getdata():
    global testdata
    for i in range(6):
        start = 100 * i
        end = 100 * (i+1)
        testdata[start:end] = np.loadtxt(f'label_{i}/sensordata_{i}.csv', delimiter=',', skiprows=1, usecols=(2,3,4), dtype=int)



def random_avg_points():
    MIN = 1150
    MAX = 2050

    for i in range(len(avgpoints)):
        point = np.array([np.random.randint(MIN, MAX),
                            np.random.randint(MIN, MAX),
                            np.random.randint(MIN, MAX)])
    
    avgpoints[i,:] = np.array(point)
        # print(avgpoints[i])


def random_avg_point(newavg):
    MIN = 1150
    MAX = 2050

    point = np.array([np.random.randint(MIN, MAX),
                        np.random.randint(MIN, MAX),
                        np.random.randint(MIN, MAX)])
    
    avgpoints[newavg,:] = np.array(point)
        # print(avgpoints[i])

# https://www.geeksforgeeks.org/maths/3d-distance-formula/
def calc_dist():
    global wonpoints_cumul
    for i in range(len(testdata)):
        distances = np.zeros(6)
        for j in range(len(avgpoints)):
            distances[j] = np.sqrt(np.sum(np.power(testdata[i] - avgpoints[j], 2)))

        closest_avgpoint_i = np.argmin(distances)
        # print(f"The closest avgpoint to measurement {i} is at index {closest_avgpoint_i}"
        #       f" with the distance of {distances[closest_avgpoint_i]}")

        wonpoints_count = int(np.max(wonpoints_cumul[closest_avgpoint_i, :, 3]))
        # print(wonpoints_count)

        cumulative = np.zeros(3)
        if (wonpoints_count > 0):
            cumulative = testdata[i] + wonpoints_cumul[closest_avgpoint_i, wonpoints_count-1, :3]
        elif (wonpoints_count == 0):
            cumulative = testdata[i]

        # Cumulation check
        # if (wonpoints_count < 3 and wonpoints_count > 0):
        #     print(f"{wonpoints_count} {testdata[i]}\n+ {wonpoints[closest_avgpoint_i, wonpoints_count-1, :3]}"
        #           f"\n= {cumulative}\n")

        # https://www.geeksforgeeks.org/python/numpy-append-python/
        wonpoints_cumul[closest_avgpoint_i, wonpoints_count, :] = np.append(cumulative, wonpoints_count+1)
        print(f"avgpoint {closest_avgpoint_i} won measurement {i}: "
              f"{wonpoints_cumul[closest_avgpoint_i, wonpoints_count, :]}")
    for k in range(len(avgpoints)):
        count = int(np.max(wonpoints_cumul[k, :, 3]))
        if(count == 0):
            random_avg_point(k)
            wonpoints_cumul = np.zeros((6, len(testdata), 4)) 
            calc_dist()
           
         


def calc_new_avg():
    for i in range(len(avgpoints)):
        count = int(np.max(wonpoints_cumul[i, :, 3]))
        cumul = np.zeros(3)
        cumul = wonpoints_cumul[i, count - 1, :3]
        avgpoints[i, :] = cumul / count
        print("aaaaaa",avgpoints[i, :3])


getdata()
random_avg_points()
calc_dist()
calc_new_avg()

colors = [
    'red', 'darkred', 'green', 'darkgreen',
    'blue', 'darkblue', 'brown'
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
        alpha=0.1
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

ax.set_title('3D Dot Cloud')
ax.legend()

ax.set_box_aspect([1, 1, 1])

plt.tight_layout()

# Linux: https://stackoverflow.com/questions/77507580/userwarning-figurecanvasagg-is-non-interactive-and-thus-cannot-be-shown-plt-sh#comment138759918_77644828
plt.show()