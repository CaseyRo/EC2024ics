import http.client

def import_matches(ROOTFOLDER,HEADERS):
    ROOTFOLDER = '/home/coder/project/datapi/py_EC2024'

    conn = http.client.HTTPSConnection("api-football-v1.p.rapidapi.com")

    conn.request("GET", "/v3/fixtures?league=4&season=2024", headers=headers)

    res = conn.getresponse()
    data = res.read()
    data = data.decode("utf-8")

    with open(f'{ROOTFOLDER}/complete_matches.json', 'w') as jsonfile:
        jsonfile.write(data)

