import requests

payload = {'groupid': '1'}
res = requests.get('http://172.20.241.9/luedataa_kannasta_groupid_csv.php', params=payload)

format = res.text.replace('\n', ';')
split = format.split(';')

# Source - https://stackoverflow.com/a/40598286
list = list(filter(None, split))

print(list)