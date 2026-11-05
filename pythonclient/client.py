import asyncio
from bleak import BleakClient
import struct
import csv

DEVICE_ADDRESS = "3702F108-47BF-B56F-90F1-DEC4E770D39B"
#USE MAC ADDRESS windows/linux!!!!!!!!
#DEVICE_ADDRESS = "D0:54:CD:D8:10:18"

with open("sensoridata.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    # Nämä otsikot helpottavat datan lukemista Pandasilla myöhemmin
    writer.writerow(["indeksi", "x", "y", "z", "dir"])

i = 0

CHARACTERISTIC_UUID = "00001526-1212-efde-1523-785feabcd123"

def notification_handler(sender: int, data: bytearray):
    global i
    print(f"Vastaanotettu {len(data)} tavua: {data}")
    val1, val2, val3, val4 = struct.unpack('<HHHH', data)
    print(f"Decoded as 4 uint16: {val1}, {val2}, {val3}, {val4}")
    i+=1
    with open("sensoridata.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([i, val1, val2, val3, val4])
        
    print(f"Tallennettu mittaus {i}: {val1}, {val2}, {val3}, {val4}")

async def main():
    
    print(f"Yhdistetään laitteeseen {DEVICE_ADDRESS}...")
    
    async with BleakClient(DEVICE_ADDRESS) as client:
        if client.is_connected:
            print("Yhteys muodostettu onnistuneesti!")
            
            print(f"Aktivoidaan ilmoitukset kanavalle {CHARACTERISTIC_UUID}...")
            await client.start_notify(CHARACTERISTIC_UUID, notification_handler)
            
            print("Kuunnellaan dataa... Paina Ctrl+C lopettaaksesi.")
            
            try:
                while True:
                    await asyncio.sleep(1)
            except asyncio.CancelledError:
                pass
            finally:
                print("Lopetetaan ilmoitusten kuuntelu...")
                await client.stop_notify(CHARACTERISTIC_UUID)
                
        else:
            print("Yhteyden muodostaminen epäonnistui.")

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("\nOhjelma suljettu.")
