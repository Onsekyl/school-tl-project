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
        
with open("sensordata.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    # Header row
    writer.writerow(["index", "x", "y", "z", "direction"])

i = 0
def notification_handler(sender: int, data: bytearray):
    global i
    print(f"Received {len(data)} bytes: {data}")
    val1, val2, val3, val4 = struct.unpack('<HHHH', data)
    print(f"Decoded as 4 uint16: {val1}, {val2}, {val3}, {val4}")
    i+=1
    with open("sensordata.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([i, val1, val2, val3, val4])
        
    print(f"Saved measurement {i}: {val1}, {val2}, {val3}, {val4}")

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
