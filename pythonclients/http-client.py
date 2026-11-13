import requests # https://docs.python-requests.org/en/latest/user/quickstart/
import os
import csv

payload = {'groupid': '1'}
FIELDS_PER_ENTRY = 12

DIRNAME = "measurements"
FILENAME = "sensordata"
EXT = ".csv"

res = requests.get('http://172.20.241.9/luedataa_kannasta_groupid_csv.php', params=payload)
# print("Received: ", res.text)
format = res.text.replace('\n', ';')
list = format.split(';')
# print("Splitted to: ", list)

path = os.path.join(os.getcwd(), DIRNAME)
try:
    print(f"Creating a subdirectory: {DIRNAME}")
    os.mkdir(path)
except FileExistsError:
    print("\tSubdirectory already exists")

print(f"Writing to a file: {DIRNAME}\\{FILENAME}{EXT}")
with open(os.path.join(path, f"{FILENAME}{EXT}"), "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    # Header row
    writer.writerow(["id", "timestamp", "groupid", "from_mac", "to_mac", "sensorvalue_a", "sensorvalue_b",
                        "sensorvalue_c", "sensorvalue_d", "sensorvalue_e", "sensorvalue_f"])
    
    start = 0
    end = FIELDS_PER_ENTRY - 1
    while (end <= len(list)):
        writer.writerow(list[start:end])
        start = end
        end += FIELDS_PER_ENTRY - 1
