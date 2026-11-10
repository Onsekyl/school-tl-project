import asyncio
from bleak import BleakClient
import mysql.connector # https://www.w3schools.com/python/python_mysql_getstarted.asp
import struct
import sys

file = open("rasp-client-secrets.txt", "r")
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

# MAC-address on Linux/Windows and UUID on Mac (Darwin).
if sys.platform == "darwin":
    DEVICE_ADDRESS = "3702F108-47BF-B56F-90F1-DEC4E770D39B"
else:
    DEVICE_ADDRESS = "D0:54:CD:D8:10:18"

CHARACTERISTIC_UUID = "00001526-1212-efde-1523-785feabcd123"

i = 0
groupid = 0
def notification_handler(sender: int, data: bytearray):
    global i
    global groupid

    # print(f"Received {len(data)} bytes: {data}")
    x, y, z, label = struct.unpack('<HHHH', data)
    # print(f"Decoded as 4 uint16: {x}, {y}, {z}, {label}")

    mycursor = mydb.cursor()
    if (i == 0):

        # Get the maximum groupid but ignore the value used for testing (9999)
        mycursor.execute("SELECT MAX(groupid) FROM rawdata HAVING MAX(groupid) < 9999")
        myresult = mycursor.fetchall()

        try:
            groupid = int(myresult[0][0]) + 1 # From the type 'list' to 'int'
        except IndexError: # No entries in the db
            groupid = 0

        # print(f"Measurement groupid will be: {groupid}")

    # Only allow the 100 measurement bursts. You can just remove the if
    # statement if you also want the 4400 measurement bursts into the db.
    if (label < 10):
        sql = "INSERT INTO rawdata (groupid, sensorvalue_x, sensorvalue_y, sensorvalue_z," \
              "sensor_direction)VALUES (%s, %s, %s, %s, %s)"
        
        val = (groupid, x, y, z, label)
        mycursor.execute(sql, val)
        mydb.commit()
        print(f"groupid: {groupid}, measurement: {i+1} inserted to db.")

    i+=1
    # print(f"Saved measurement {i}: {x}, {y}, {z}, {label}")

    if (label < 10 and i >= 100):
        i = 0
    elif (i >= 4400):
        i = 0

async def main():
    
    print(f"Connecting to a device: {DEVICE_ADDRESS}...")
    
    async with BleakClient(DEVICE_ADDRESS) as client:
        if client.is_connected:
            print("Connection established!")
            
            print(f"Subscribing notifications from a characteristic: {CHARACTERISTIC_UUID}...")
            await client.start_notify(CHARACTERISTIC_UUID, notification_handler)
            
            print("Listening for notifications... Ctrl+C to stop.")
            
            try:
                while True:
                    await asyncio.sleep(1)
            except asyncio.CancelledError:
                pass
            finally:
                print("Unsubscribing from notifications...")
                await client.stop_notify(CHARACTERISTIC_UUID)
                
        else:
            print("Failed to establish connection.")

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("\nProgram closed.")
