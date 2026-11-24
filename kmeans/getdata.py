import mysql.connector # https://www.w3schools.com/python/python_mysql_getstarted.asp
import os
import csv

file = open("mysql-read-secrets.txt", "r")
user = file.readline().strip()
password = file.readline().strip()
file.close()

mydb = mysql.connector.connect(
    host="172.20.241.128",
    user=user,
    password=password,
    database="measurements"
)
print(mydb) 

mycursor = mydb.cursor()
mycursor.execute("SELECT * FROM rawdata")
myresult = mycursor.fetchall()

FILENAME = "sensordata_"
EXT = ".csv"

last_groupid = -1
last_label = -1
path = ''
for row in myresult:
    # print(row)
    id, groupid, x, y, z, label = row
    # print(id, groupid, x, y, z, direction)

    if (label != last_label):
        last_label = label
        path = os.path.join(os.getcwd(), f'label_{label}')
    
        try:
            # print(f"Creating a subdirectory: label_{label}")
            os.mkdir(path)
        except FileExistsError:
            # print("\tSubdirectory already exists")
            pass # https://stackoverflow.com/a/574734

    if (groupid != last_groupid):
        last_groupid = groupid
        with open(os.path.join(path, f"{FILENAME}{groupid}{EXT}"), "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            # Header row
            writer.writerow(["id", "groupid", "x", "y", "z", "direction"])


    with open(os.path.join(path, f"{FILENAME}{groupid}{EXT}"), "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([id, groupid, x, y, z, label])

f.close()
