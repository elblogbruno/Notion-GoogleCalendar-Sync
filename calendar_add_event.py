from calendar_api import google_calendar_api 
from time import sleep

m = google_calendar_api() 
calendar_id = m.list_available_calendars()
# m.get_upcoming_events()
event_id = m.create_event(calendar_id=calendar_id, start='2020-12-5T15:00:00.603111+00:00', end='2020-12-5T15:00:00.603111+00:00',description='foo',summary='Demo Event')
sleep(10)
m.update_event(calendar_id=calendar_id,event_id=event_id, start='2020-12-5T15:00:00.603111+00:00', end='2020-12-61T15:00:00.603111+00:00',description='cabronb1')

m.get_upcoming_events()
