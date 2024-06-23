import http.client
import requests
import requests_cache

def import_matches(ROOTFOLDER,HEADERS):

    requests_cache.install_cache('all_match_cache', expire_after=3600)

    conn = http.client.HTTPSConnection("api-football-v1.p.rapidapi.com")

    conn.request("GET", "/v3/fixtures?league=4&season=2024", headers=HEADERS)

    res = conn.getresponse()
    data = res.read()
    data = data.decode("utf-8")

    with open(f'{ROOTFOLDER}/complete_matches.json', 'w') as jsonfile:
        jsonfile.write(data)

