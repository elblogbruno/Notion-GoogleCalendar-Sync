import json
import os

from notion.client import NotionClient
from notion.collection import CalendarView
from notion.block import BasicBlock
from notion.user import User
from notion.collection import NotionDate

from time import sleep
from gtasks import Gtasks

from utils.task_utils import *
from utils.notion_utils import * 

from datetime import timedelta
from datetime import datetime as dt
from tzlocal import get_localzone

gt = Gtasks()

###
### Sync notion tasks with google tasks 
###
def sync_notion_to_tasks(client, calendar_url, title_format,list_id):
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

    
    tasks = gt.get_tasks(task_list=list_id)
    print("Entries on notion calendar: " + str(len(calendar_entries)))
    print("Entries on google tasks: " + str(len(tasks)))

    for e in calendar_entries:
        date = e.get_property(dateprop['id'])
        if date is None:
            continue
        
        name = e.get_property(title_prop['id'])
        clean_props = {'NAME': name}
        

        desc = ''
        desc += e.get_browseable_url() + '\n\n'
        desc += 'Properties:\n'
        for k, v in e.get_all_properties().items():
            if k != dateprop['slug']:
                name = properties_by_slug[k]['name']
                desc += "  - {}: {}\n".format(name, v)
                clean_props[name] = v
        title = title_format.format_map(clean_props)

        start_format = date._format_datetime(date.start)
        if start_format[1] == None: #no time specified on the date.
            date.start =  date._parse_datetime(str(date.start),"00:00")
        print(e.status)
        if(e.status == "Done"):
            print("Status is  done, so it has finished!")
            remove_task_from_list(gt,list_id,title,date.start,date.end)
        else:
            print("Status is not done, so it has not been finished! A")
            add_task_to_list(gt,list_id,title,date.start,date.end,desc)
        # Print
        # print("{}: {} -> {}".format(title, date.start,date.end))
        # print(desc)
        # print('--------------')

###
### Sync new google tasks with notion 
###
def sync_gtasks_to_notion(client, calendar_url, title_format,list_id):
    calendar = client.get_block(calendar_url)
    for view in calendar.views:
        if isinstance(view, CalendarView):
            calendar_view = view
            break
    else:
        raise Exception(f"Couldn't find a calendar view in the following list: {calendar.views}")
    calendar_query = calendar_view.build_query()
    calendar_entries = calendar_query.execute()

    ten_mins_ago = dt.now() - timedelta(minutes=5)

    tasks = gt.get_tasks(task_list=list_id,updated_min=ten_mins_ago)  
    
    print("Entries on notion calendar: " + str(len(calendar_entries)))
    print("Entries on google tasks: " + str(len(tasks)))

    if len(tasks) > 0:
        for task in tasks:
            entry = search_task_on_notion(calendar_entries,task.title)
            if entry:
                print("Task exists on notion")
            else:
                print("New task is not on notion")
                # notion_event = calendar.collection.add_row() 
                # notion_event.name = task.title
                # new_date = NotionDate(str(task.due_date))
                # new_date.end = str(task.completion_date)
                # print(notion_event)

    
def main():
    with open('settings.json') as f:
        settings = json.load(f)
        token = settings['token']
        url = settings['url']
        client = NotionClient(settings['token'], monitor=False)
    
    list_id = ""
    if os.path.isfile("prioritary-list.txt"):
        f = open("prioritary-list.txt", "r")
        list_id = f.read()
        f.close()
        print("List was choosen already, gonna sync this {0} list!".format(list_id))
    else:
        list_id = list_available_lists()
        f = open("prioritary-list.txt", "a")
        f.write(list_id)
        f.close()
        print("Prioritary sync list was set to this {0} list!".format(list_id))

    
    sync_gtasks_to_notion(client,url,"{NAME}",list_id)
    sync_notion_to_tasks(client,url,"{NAME}",list_id)

if __name__ == "__main__":
    main()

