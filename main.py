# -*- coding: utf-8 -*-

from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import datetime

import requests
import json
from bs4 import BeautifulSoup

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'

DATES_POST_URL = "http://ekosystem.wroc.pl/admin/admin-ajax.php"
DATES_DATA = {'action': 'harmonogram_nowy_step2', 'id_numeru': 375877}

CALENDAR_ADDRESS = "a55ujg5sn58h6cege4qvqh595c@group.calendar.google.com"  # Wywóz śmieci


event_template = {
    'summary': 'Szkło',
    'location': 'Moniuszki 34, Wrocław',
    'start': {
        'date': '2018-04-08'
    },
    'end': {
        'date': '2018-04-09'
    },
    'reminders': {
        'useDefault': False,
        'overrides': [
            {'method': 'popup', 'minutes': 6 * 60},
        ],
    },
}


def get_dates():

    r = requests.post(DATES_POST_URL, data=DATES_DATA)
    print(r.status_code, r.reason)

    r_json = json.loads(r.text)

    bs = BeautifulSoup(r_json['wiadomoscRWD'], "lxml")
    rows = bs.table.tbody.findAll('td')

    data = [row.string.replace('<td>', '').replace('</td>', '')
            for row in rows]

    return data


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:  # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def main():
  global event_template

  credentials = get_credentials()
  http = credentials.authorize(httplib2.Http())
  service = discovery.build('calendar', 'v3', http=http)

  data = get_dates()

  summary = ""

  for row in data:
    if row == u'szk\u0142o':
      summary = "Szkło"
      print(summary)
    elif row == u'zielone':
      summary = "Odpady zielone"
      print(summary)
    elif row == u'zmieszane':
      summary = "Zmieszane"
      print(summary)
    elif row == u'tworzywa':
      summary = "Tworzywa sztuczne"
      print(summary)
    elif row == u'papier':
      summary = "Papier"
      print(summary)
    else:
      print(row)
      event_template['summary'] = summary
      start_date = datetime.datetime.strptime(row, "%Y-%m-%d").date()
      end_date = start_date + datetime.timedelta(days=1)
      event_template['start']['date'] = start_date.strftime("%Y-%m-%d")
      event_template['end']['date'] = end_date.strftime("%Y-%m-%d")
    
      event = service.events().insert(calendarId=CALENDAR_ADDRESS, body=event_template).execute()
      print("Event created:  {}".format(event.get("htmlLink")))

if __name__ == '__main__':
    main()
