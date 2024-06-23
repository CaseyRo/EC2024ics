import http.client
import os
import requests
import requests_cache

from dotenv import load_dotenv

def get_details(ROOTFOLDER,HEADERS,MATCHID):

    requests_cache.install_cache('match_cache', expire_after=3600)

    conn = http.client.HTTPSConnection("api-football-v1.p.rapidapi.com")

    conn.request("GET", f"/v3/fixtures?id={MATCHID}", headers=HEADERS)

    res = conn.getresponse()
    data = res.read()
    data = data.decode("utf-8")

    # print(f"{data}")

    with open(f'{ROOTFOLDER}matches/{MATCHID}.json', 'w') as jsonfile:
        jsonfile.write(data)

load_dotenv()

ROOTFOLDER = os.environ.get('ROOTFOLDER')
DEPLOYFOLDER = os.environ.get('DEPLOYFOLDER')

HEADERS = {
    'X-RapidAPI-Key': os.environ.get('XRAPIDAPIKEY'),
    'X-RapidAPI-Host': os.environ.get('XRAPIDAPIHOST')
}

# get_details(ROOTFOLDER,HEADERS,1145509)

