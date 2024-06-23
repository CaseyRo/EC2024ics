from rich.console import Console
from rich.markdown import Markdown
from icalendar import Calendar, Event,vDate
from datetime import datetime, timedelta
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

import pytz, json
import import_data, get_detailed_match_report, get_fixtures
import os
import sys
import argparse

load_dotenv()

ROOTFOLDER = os.environ.get('ROOTFOLDER')
DEPLOYFOLDER = os.environ.get('DEPLOYFOLDER')
DEBUG = False
groupscal = {}

HEADERS = {
    'X-RapidAPI-Key': os.environ.get('XRAPIDAPIKEY'),
    'X-RapidAPI-Host': os.environ.get('XRAPIDAPIHOST')
}

import_data.import_matches(ROOTFOLDER,HEADERS)
get_fixtures.get_fixtures(ROOTFOLDER,HEADERS)

def main(parameter):
    global DEBUG
    # print(f"Received parameter: {parameter}")
    if parameter == 'debug':
        print ("Debug mode is on")
        DEBUG = True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A script that accepts a parameter.")
    parser.add_argument("parameter", type=str, nargs='?', default=None, help="add 'debug' to run in debug mode")

    args = parser.parse_args()
    main(args.parameter)

# Function to convert string time to datetime object
def str_to_datetime(date, time_compensation):

    # Parse the string into a datetime object
    dt = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S+00:00")

    # Apply the time compensation
    dt += timedelta(hours=time_compensation)

    # Set the timezone to UTC
    utc_tz = pytz.timezone('UTC')
    dt = utc_tz.localize(dt)

    return dt

def string_to_number_hash(s):
    return hash(s)

# creates all group events with results for the group
def create_groupEvent(onDay,matchDetails):
    global groupscal, groupResults, ROOTFOLDER, HEADERS, DEBUG

    matchDetails['onDay'] = onDay
    matchDetails['rankings'] = groupResults
    # jsonprint (matchDetails)
    group_template = env.get_template('group_summary.j2')
    groupsummary = group_template.render(matchDetails)
    groupscal[matchDetails['group']] = {"summary": f'⚽ {matchDetails["group"]} standings',
                                        "description": f'{groupsummary}',
                                        "date": onDay,
                                        "url": matchDetails['groupUrl']}
    # if DEBUG: print(f'{groupscal[matchDetails["group"]]}')

def jsonprint(uglyjson):
    print(json.dumps(uglyjson, indent=4))

# Load match data from JSON file
with open(f'{ROOTFOLDER}/complete_matches.json', 'r') as file:
    matches = json.load(file)

with open(f'{ROOTFOLDER}/teams.json', 'r') as file:
    teams = json.load(file)

with open(f'{ROOTFOLDER}/locations.json', 'r') as file:
    locations = json.load(file)

with open(f'{ROOTFOLDER}/locations_moreinfo.json', 'r') as file:
    locations_moreinfo = json.load(file)

with open(f'{ROOTFOLDER}/fixtures.json', 'r') as file:
    groupResults = json.load(file)

# Create a calendar
cal = Calendar()
cal.add('prodid', '-//CDIT//UEFA Euro 2024 Calendar//EN//')
cal.add('version', '2.0')
cal.add('summary', 'UEFA Euro 2024 Germany')
cal.add('description', 'All matches, results updated daily. \nBrought to you by Casey.berlin')

# Create an event
for index, match in enumerate(matches['response'],start=1):
    MATCHDURATION = 2
    moreInfoUrl = ""
    groupUrl = "https://www.uefa.com/euro2024/standings/"
    address = ""
    MATCHID = match['fixture']['id']
    matchdetails = {'events':{},'groupUrl':groupUrl,'league':{},'fixture':{'venue':{}},'home':{},'away':{},'goals' : {'home':0,'away':0}, 'group': ""}
    if DEBUG: matchdetails['id'] = MATCHID

    matchdetails['league']['name'] = match['league']['name']
    matchdetails['league']['season'] = match['league']['season']
    matchdetails['league']['round'] = match['league']['round']
    matchdetails['fixture']['venue']['name'] = match['fixture']['venue']['name']
    matchdetails['fixture']['venue']['city'] = match['fixture']['venue']['city']

    basicuid = f"20240503T160000Z-{MATCHID}@EURO2024.casey.berlin"

    for team in teams:
        if (match['teams']['home']['name'] == team['Name']):
            matchdetails['group'] = f"group {team['Group']}"
            matchdetails['home'] = {
                'name': team['Name'],
                'id': match['teams']['home']['id'],
                'flag': team['Flag']
            }
        if (match['teams']['away']['name'] == team['Name']):
            matchdetails['away'] = {
                'name' : team['Name'],
                'id' : match['teams']['away']['id'],
                'flag': team['Flag']
            }
    if match['fixture']['status']['short'] in ["FT","AET","PEN"]:
        file_path = Path(f"matches/{MATCHID}.json")
        if not file_path.exists():
            get_detailed_match_report.get_details(ROOTFOLDER,HEADERS,MATCHID)
        with open(f'{ROOTFOLDER}/matches/{MATCHID}.json', 'r') as file:
            match_file = json.load(file)

        # print(f"here's file number {index}\n{match_file}\n------")
        # print (f"{match_file['response'][0]['events'][0]}")
        myevents = 0

        for index, event in enumerate(match_file['response'][0]['events'],start=1):
            if event['type'] in ["Goal"]:
                matchdetails['events'][myevents] = {}
                curevent = matchdetails['events'][myevents]
                curevent['time'] = event['time']['elapsed']
                curevent['team'] = event['team']['id']
                if curevent['team'] == matchdetails['home']['id']:
                    matchdetails['goals']['home'] += 1
                else:
                    matchdetails['goals']['away'] += 1
                curevent['score'] = f"{matchdetails['goals']['home']}-{matchdetails['goals']['away']}"
                curevent['player'] = event['player']['name']
                curevent['assist'] = event['assist']['name']
                curevent['type'] = event['type']
                curevent['detail'] = event['detail']

                myevents += 1



    matchdetails['homescore'] = f"{match['goals']['home']}" if match['goals']['home'] is not None else None
    matchdetails['awayscore'] = f"{match['goals']['away']}" if match['goals']['away'] is not None else None
    matchdetails['halftimescore'] = f"{match['score']['halftime']['home']} - {match['score']['halftime']['away']}" if match['score']['halftime']['home'] is not None else None

    env  = Environment(loader=FileSystemLoader('.'))
    summary_template = env.get_template('template.j2')
    SUMMARY = summary_template.render(matchdetails)

    description_template = env.get_template('description.j2')
    # print(matchdetails)
    DESCRIPTION = description_template.render(matchdetails)

    # print(SUMMARY)
    # break

    for location in locations:
        if (match['fixture']['venue']['name'].lower() in location['Location'].lower()):
            moreInfoUrl = location['More info']
        for locations_moreinfo_item in locations_moreinfo['response']:
            if locations_moreinfo_item['name']:
                if match['fixture']['venue']['name'].lower() in locations_moreinfo_item['name'].lower():
                    address = f"{locations_moreinfo_item['address']}, {locations_moreinfo_item['city']}"

    if moreInfoUrl == "":
        print("error on " + match['fixture']['venue']['name'])
    if globals().get('address', "") == "":
        print("address error on " + match['fixture']['venue']['name'])

    event = Event()
    event['uid'] = basicuid
    event.add('summary', SUMMARY)

    matchday = match['fixture']['date']

    event.add('dtstart', str_to_datetime(matchday,0))
    event.add('dtend', str_to_datetime(matchday,MATCHDURATION))
    event.add('dtstamp', datetime.now(pytz.utc))
    event.add('location', f"{address}")
    event.add('url',moreInfoUrl)

    event.add('description', DESCRIPTION)
    # print(event)

    # create rankings event
    create_groupEvent(matchday,matchdetails)
    # Add event to the calendar
    cal.add_component(event)

for group_name,calendars in groupscal.items():
    if DEBUG: print(calendars)
    event2 = Event()
    hash_2 = hash(calendars['summary'])
    event2['uid'] = f"20240503T160000Z-{hash_2}@EURO2024.casey.berlin"
    event2.add('summary', calendars['summary'])
    date_time_obj = datetime.strptime(calendars['date'], '%Y-%m-%dT%H:%M:%S%z')

# Extract the year, month, and day
    year = date_time_obj.year
    month = date_time_obj.month
    day = date_time_obj.day
    startdate = datetime(year,month,day)
    startdate = vDate(startdate)
    event2.add('dtstart', startdate)
    # event2.add('duration', 'dur-day')

    event2.add('url',calendars['url'])
    event2.add('description', calendars['description'])

    cal.add_component(event2)

# Write the calendar to an ics file
with open(f'{DEPLOYFOLDER}/euro2024.ics', 'wb') as ics_file:
    ics_file.write(cal.to_ical())

print("ICS file has been created.")
