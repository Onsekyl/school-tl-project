import requests # https://docs.python-requests.org/en/latest/user/quickstart/

FIELDS_PER_ENTRY = 12

payload = {'groupid': '1'}
res = requests.get('http://172.20.241.9/luedataa_kannasta_groupid_csv.php', params=payload)
format = res.text.replace('\n', ';')
split = format.split(';')

i = 0
for field in split:
    if (i  == FIELDS_PER_ENTRY - 1):
        print('') # Newline
        i = 0

    print(f"{field} ", end='')
    i += 1
    