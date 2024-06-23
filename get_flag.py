from dotenv import load_dotenv
import json,os

load_dotenv()

ROOTFOLDER = os.environ.get('ROOTFOLDER')

with open(f'{ROOTFOLDER}/teams.json', 'r') as file:
    teams = json.load(file)

def get_flag(get_team):
    for team in teams:
        if team['Name'] == get_team:
            return team['Flag']
