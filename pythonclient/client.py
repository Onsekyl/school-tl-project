import asyncio
from bleak import BleakClient
import struct
import csv
import os

# MAC-address on Linux/Windows and UUID on Mac (Darwin).
if (os.name == "Darwin"):
    DEVICE_ADDRESS = "3702F108-47BF-B56F-90F1-DEC4E770D39B"
else:
    DEVICE_ADDRESS = "D0:54:CD:D8:10:18"

CHARACTERISTIC_UUID = "00001526-1212-efde-1523-785feabcd123"

i = 0
j = 0
def notification_handler(sender: int, data: bytearray):
    global i
    global j
    global path
    FILENAME = "sensordata_"
    EXT = ".csv"

    # print(f"Received {len(data)} bytes: {data}")
    x, y, z, label = struct.unpack('<HHHH', data)
    # print(f"Decoded as 4 uint16: {x}, {y}, {z}, {label}")

    if (i == 0):
        path = os.path.join(os.getcwd(), f'label_{label}')
        
        try:
            print(f"Creating a subdirectory: label_{label}")
            os.mkdir(path)
        except FileExistsError:
            print("\tSubdirectory already exists")

        file_created = False
        while (not file_created):
            try:
                print(f"Creating a file: label_{label}\\{FILENAME}{j}{EXT}")
                open(os.path.join(path, f"{FILENAME}{j}{EXT}"), "x")
            except FileExistsError:
                print(f"\tlabel_{label}\\{FILENAME}{j}{EXT} already exists, incrementing")
                j+=1
                continue
            
            print(f"File created: label_{label}\\{FILENAME}{j}{EXT}")
            file_created = True
        
        with open(os.path.join(path, f"{FILENAME}{j}{EXT}"), "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            # Header row
            writer.writerow(["x", "y", "z"])
    
    with open(os.path.join(path, f"{FILENAME}{j}{EXT}"), "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([x, y, z])
    
    i+=1
    print(f"Saved measurement {i}: {x}, {y}, {z}, {label}")

    if (label < 10 and i >= 100):
        i = 0
        j = 0
    elif (i >= 4400):
        i = 0
        j = 0

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
