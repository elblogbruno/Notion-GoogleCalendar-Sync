import json
from datetime import datetime

from icalendar import Calendar, Event
from notion.client import NotionClient
from notion.collection import CalendarView
from notion.block import BasicBlock
from notion.user import User

from calendar_api import google_calendar_api 
from time import sleep

from dateutil.parser import parse as dtparse
from datetime import datetime as dt
from tzlocal import get_localzone
m = google_calendar_api() 

def get_ical(client, calendar_url, title_format,google_calendar_id):
    calendar = client.get_block(calendar_url)
    for view in calendar.views:
        if isinstance(view, CalendarView):
            calendar_view = view
            break
    else:
        raise Exception(f"Couldn't find a calendar view in the following list: {calendar.views}")
    #print(calendar_view.get('query2')['calendar_by'])
    #print(calendar_view.get())
    calendar_query = calendar_view.build_query()
    calendar_entries = calendar_query.execute()

    collection = calendar.collection

    schema = collection.get_schema_properties()

    properties_by_name = {}
    properties_by_slug = {}
    properties_by_id = {}
    title_prop = None

    for prop in schema:
        name = prop['name']
        if name in properties_by_name:
            print("WARNING: duplicate property with name {}".format(name))
        properties_by_name[name] = prop
        properties_by_slug[prop['slug']] = prop
        properties_by_id[prop['id']] = prop
        if prop['type'] == 'title':
            title_prop = prop
            
    assert title_prop is not None, "Couldn't find a title property"

    dateprop = properties_by_id[calendar_query.calendar_by]
    #assert dateprop['type'] == 'date', "Property '{}' is not a Date property".format(settings['property'])

    cal = Calendar()
    cal.add("summary", "Imported from Notion, via notion-export-ics.")
    cal.add('version', '2.0')
    
    for e in calendar_entries:
        date = e.get_property(dateprop['id'])
        if date is None:
            continue
        
        name = e.get_property(title_prop['id'])
        clean_props = {'NAME': name}
        
        # Put in ICS file
        event = Event()
        desc = ''
        event.add('dtstart', date.start)
        if date.end is not None:
            event.add('dtend', date.end)
        desc += e.get_browseable_url() + '\n\n'
        desc += 'Properties:\n'
        for k, v in e.get_all_properties().items():
            if k != dateprop['slug']:
                name = properties_by_slug[k]['name']
                desc += "  - {}: {}\n".format(name, v)
                clean_props[name] = v
        title = title_format.format_map(clean_props)
        event.add('summary', title)
        event.add('description', desc)
        cal.add_component(event)

        start_format = date._format_datetime(date.start)
        if start_format[1] == None: #no time specified on the date.
            date.start =  date._parse_datetime(str(date.start),"00:00")

        event_id = m.create_event(calendar_id=google_calendar_id, start=date.start, end=date.end,timezone=str(get_localzone()),description=desc,summary=title)

        # Print
        print("{}: {} -> {}".format(title, date.start,date.end))
        print(desc)
        print('--------------')
    
    return cal

def remove_done_tasks(client, calendar_url, title_format,google_calendar_id):
    calendar = client.get_block(calendar_url)
    for view in calendar.views:
        if isinstance(view, CalendarView):
            calendar_view = view
            break
    else:
        raise Exception(f"Couldn't find a calendar view in the following list: {calendar.views}")

    calendar_query = calendar_view.build_query()
    calendar_entries = calendar_query.execute()

    collection = calendar.collection

    schema = collection.get_schema_properties()

    properties_by_name = {}
    properties_by_slug = {}
    properties_by_id = {}
    title_prop = None

    for prop in schema:
        name = prop['name']
        if name in properties_by_name:
            print("WARNING: duplicate property with name {}".format(name))
        properties_by_name[name] = prop
        properties_by_slug[prop['slug']] = prop
        properties_by_id[prop['id']] = prop
        if prop['type'] == 'title':
            title_prop = prop
            
    assert title_prop is not None, "Couldn't find a title property"

    dateprop = properties_by_id[calendar_query.calendar_by]
    #assert dateprop['type'] == 'date', "Property '{}' is not a Date property".format(settings['property'])

    
    for e in calendar_entries:
        date = e.get_property(dateprop['id'])
        if date is None:
            continue
        
        name = e.get_property(title_prop['id'])
        clean_props = {'NAME': name}

        for k, v in e.get_all_properties().items():
            if k != dateprop['slug']:
                name = properties_by_slug[k]['name']
                clean_props[name] = v
        title = title_format.format_map(clean_props)
        deleted = False
        print(str(title))
        if(e.status == "Done"):
            deleted = m.remove_event(calendar_id=google_calendar_id, min=date.start, max=date.end,start_date=date.start,event_summary=title)
        else:
            print("Status is not done, so it has not been finished!")
        if deleted:
            print("Event was deleted")
    return deleted
if __name__ == "__main__":

    with open('settings.json') as f:
        settings = json.load(f)
        token = settings['token']
        url = settings['url']
        client = NotionClient(settings['token'], monitor=False)
    calendar_id = m.list_available_calendars()
    
    remove_done_tasks(client,url,"{NAME}",calendar_id)
    cal = get_ical(client,url,"{NAME}",calendar_id)

