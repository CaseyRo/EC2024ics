from rich.console import Console
from rich.markdown import Markdown
from icalendar import Calendar, Event
from datetime import datetime, timedelta
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader

import pytz, json
import import_data
import os

load_dotenv()

ROOTFOLDER = os.environ.get('ROOTFOLDER')
DEPLOYFOLDER = os.environ.get('DEPLOYFOLDER')

HEADERS = {
    'X-RapidAPI-Key': os.environ.get('XRAPIDAPIKEY'),
    'X-RapidAPI-Host': os.environ.get('XRAPIDAPIHOST')
}

# import_data.import_matches(ROOTFOLDER,HEADERS)

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

# Load match data from JSON file
with open(f'{ROOTFOLDER}/complete_matches.json', 'r') as file:
    matches = json.load(file)

with open(f'{ROOTFOLDER}/teams.json', 'r') as file:
    teams = json.load(file)

with open(f'{ROOTFOLDER}/locations.json', 'r') as file:
    locations = json.load(file)

with open(f'{ROOTFOLDER}/locations_moreinfo.json', 'r') as file:
    locations_moreinfo = json.load(file)

# Create a calendar
cal = Calendar()
cal.add('prodid', '-//CDIT//UEFA Euro 2024 Calendar//EN//')
cal.add('version', '2.0')
cal.add('summary', 'UEFA Euro 2024 Germany')
cal.add('description', 'All matches, results updated daily. \nBrought to you by Casey.berlin')

# Create an event
for match in matches['response']:
    MATCHDURATION = 2
    moreInfoUrl = ""
    matchdetails = {}

    basicuid = f"20240503T160000Z-{match['fixture']['id']}@EURO2024.casey.berlin"

    for team in teams:
        if (match['teams']['home']['name'] == team['Name']):
            matchdetails['group'] = f"(group {team['Group']})"
            matchdetails['home'] = f"{team['Flag']} {team['Name']}"
        if (match['teams']['away']['name'] == team['Name']):
            matchdetails['away'] = f"{team['Name']} {team['Flag']}"

    matchdetails['homescore'] = f'{match['goals']['home']}' if match['goals']['home'] else None
    matchdetails['awayscore'] = f'{match['goals']['away']}' if match['goals']['away'] else None
    matchdetails['halftimescore'] = f'{match['score']['halftime']['home']} - {match['score']["halftime"]["away"]}' if match['score']['halftime']['home'] else None

    env  = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('template.j2')
    SUMMARY = template.render(matchdetails)

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
    if address == "":
        print("address error on " + match['fixture']['venue']['name'])

    event = Event()
    event['uid'] = basicuid
    event.add('summary', SUMMARY)
    event.add('dtstart', str_to_datetime(match['fixture']['date'],0))
    event.add('dtend', str_to_datetime(match['fixture']['date'],MATCHDURATION))
    event.add('dtstamp', datetime.now(pytz.utc))
    event.add('location', f"{address}")
    event.add('url',moreInfoUrl)
    event.add('description', f"""{match['league']['name']} {match['league']['season']}
              \n{match['fixture']['venue']['name']}, {match['fixture']['venue']['city']}
              \n{match['league']['round']}""")

    # Add event to the calendar
    cal.add_component(event)

# Write the calendar to an ics file
with open(f'{DEPLOYFOLDER}/euro2024.ics', 'wb') as ics_file:
    ics_file.write(cal.to_ical())

print("ICS file has been created.")
