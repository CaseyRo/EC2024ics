import http.client
import os
import argparse
import json
import requests
import requests_cache
import get_flag

from dotenv import load_dotenv

DEBUG = False

def get_fixtures(ROOTFOLDER,HEADERS):
    global DEBUG
    conn = http.client.HTTPSConnection("api-football-v1.p.rapidapi.com")
    requests_cache.install_cache('fixture_cache', expire_after=3600)
    conn.request("GET", f"/v3/standings?league=4&season=2024", headers=HEADERS)

    res = conn.getresponse()
    data = res.read()
    data = data.decode("utf-8")
    jsondata = json.loads(data)

    # if DEBUG: print(f"{jsondata}\n\n-----\n")

    # with open(f'{ROOTFOLDER}fixtures.json', 'w') as jsonfile:
    #     jsonfile.write(data)

    # with open(f'{ROOTFOLDER}fixtures.json', 'r') as jsonfile:
    #     standings = json.load(jsonfile)
    #     standings = standings["response"][0]["league"]["standings"]

    newStanding = {}
    for standing in jsondata["response"][0]["league"]["standings"]:
        for team in iter(standing):
            if DEBUG: print(team)
            key = team['group']
            groupinfo = {
                "rank": team['rank'],
                "team": team['team']['name'],
                "points": team['points'],
                "goalsDiff": team['goalsDiff'],
                "form": team['form'],
                "flag": get_flag.get_flag(team['team']['name'])
            }

            if not key in newStanding:
                newStanding[key] = []
            newStanding[key].append(groupinfo)

    # if DEBUG: print(newStanding)

    with open(f'{ROOTFOLDER}fixtures.json', 'w') as jsonfile:
        jsonfile.write(json.dumps(newStanding))

def main(parameter):
    global DEBUG
    # print(f"Received parameter: {parameter}")
    if parameter == 'debug':
        load_dotenv()

        ROOTFOLDER = os.environ.get('ROOTFOLDER')

        HEADERS = {
            'X-RapidAPI-Key': os.environ.get('XRAPIDAPIKEY'),
            'X-RapidAPI-Host': os.environ.get('XRAPIDAPIHOST')
        }
        print ("Debug mode is on")
        DEBUG = True
        get_fixtures(ROOTFOLDER,HEADERS)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A script that accepts a parameter.")
    parser.add_argument("parameter", type=str, nargs='?', default=None, help="add 'debug' to run in debug mode")

    args = parser.parse_args()
    main(args.parameter)



