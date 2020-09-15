from __future__ import print_function
import datetime
import pickle
import os.path
import json
from json import dumps
from datetime import date, datetime

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.events','https://www.googleapis.com/auth/calendar']

class google_calendar_api:
    def __init__(self):
        """Shows basic usage of the Google Calendar API.
        Prints the start and name of the next 10 events on the user's calendar.
        """
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('calendar', 'v3', credentials=creds)

    def json_serial(self,obj):
        """JSON serializer for objects not serializable by default json code"""
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        raise TypeError ("Type %s not serializable" % type(obj))
    def create_event(self, calendar_id, start, end,timezone, description,summary):
        print("{}: {} -> {}".format(summary, start, end))
        start = dumps(start, default=self.json_serial).replace('"', '')

        if end == None:
            print("No end date")
            end = start.replace('"', '')
        else:
            end = dumps(end, default=self.json_serial).replace('"', '')
        
        event = {
            'description':description,
            'summary':summary,
            'start':{'dateTime': start,'timeZone':timezone},
            'end':{'dateTime': end,'timeZone':timezone},
        }
        
        #print(event)
        if self.event_exists(calendar_id,start,end,start,summary) == False:
            event = self.service.events().insert(calendarId=calendar_id, body=event).execute()
            print ('Event created: %s' % (event.get('htmlLink')))
        else:
            event = self.event
            print ("Event already exists")
        return event['id']

    def event_exists(self,calendar_id,min,max,start_date,event_summary):
        print("Checking if {0} event exists: {1} {2}".format(event_summary,min,max))
        events_result = self.service.events().list(calendarId=calendar_id, singleEvents=True,orderBy='startTime').execute()
        
        events = events_result.get('items', [])
        found = False
        #print(events)
        if not events:
            print('Event does not exist yet.')
        else:
            found = False
            for event in events:
                #print(event)
                start = event['start'].get('dateTime', event['start'].get('date'))
                summary = "X" if 'summary' not in event else str(event['summary'])
                if start == start_date or str(summary) == str(event_summary):
                    found = True
                    self.event = event
                    print('Event has been found.')
                    break
            if found != True:
                print('Event does not exist yet.')
        return found
    def update_event(self,calendar_id, event_id, start, end, description):
        try:
            event = self.service.events().get(calendarId=calendar_id, eventId=event_id).execute()
        except HttpError as e:
            if e.resp.status==404:
                return self.create_event(calendar_id, start, end, description)

        event["start"]={'dateTime':start}
        event["end"]={'dateTime':end}
        event["summary"]= description
        event["description"]= description
        updated_event = self.service.events().update(calendarId=calendar_id, eventId=event_id, body=event).execute()
        return updated_event["id"]
    def get_upcoming_events(self,maxEvents = 10):
         # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
        print('Getting the upcoming 10 events')
        events_result = self.service.events().list(calendarId='primary', timeMin=now,
                                            maxResults=maxEvents, singleEvents=True,
                                            orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])
    def list_available_calendars(self):
        calendars_available = self.service.calendarList().list().execute()
        
        calendar_id = []
        calendar_names = []

        i = 1
        print("These are your avaliable calendars, please choose one: ")
        for calendar in calendars_available['items']:
            print("{0}) {1}".format(i,calendar['summary'].encode('utf8')))
            calendar_id.append(calendar['id'])
            calendar_names.append(calendar['summary'])
            i=i+1
        calendar_index = input("Choose a calendars by the number: ")

        while int(calendar_index) < 0 or int(calendar_index) > len(calendar_id):
            print(calendar_index)
            print("Choose a playlist available on the list.")
            calendar_index = input("Choose a playlist by the number: ")

        print ("Gonna syncronize notion tasks with this calendar {0}".format(calendar_names[int(calendar_index)-1]))
        
        final_id = calendar_id[int(calendar_index)-1]
        
        return final_id
    def remove_event(self,calendar_id,min,max,start_date,event_summary):
        print("Removing {0} event : {1} {2}".format(event_summary,min,max))
        events_result = self.service.events().list(calendarId=calendar_id, singleEvents=True,orderBy='startTime').execute()
        
        events = events_result.get('items', [])
        found = False
        #print(events)
        if not events:
            print('Event does not exist yet.')
        else:
            found = False
            for event in events:
                #print(event)
                start = event['start'].get('dateTime', event['start'].get('date'))
                summary = "X" if 'summary' not in event else str(event['summary'])
                if start == start_date or str(summary) == str(event_summary):
                    found = True
                    event_id = event['id']
                    delete_body =  {
                        "calendarId" : calendar_id,
                        "eventId" : event_id,
                        "sendUpdates"  : "all",
                    }
                    self.service.events().delete(**delete_body)
                    print('Event has been found.')
                    break
            if found != True:
                print('Event does not exist yet.')
        return found