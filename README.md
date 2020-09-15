# Notion-GoogleCalendar-Sync
This project allows you to sync a notion database with a calendar view with the google calendar.

Need to have a ```client_id.json``` get from the Google Calendar API, more info here: 
https://developers.google.com/calendar/quickstart/python

Also a ```settings.json``` file with this structure:
```
{
	"token":"xxxxxxxxx", # token_v2, it can be get from the cookies
	"url":"XXXXXXXXX",  #calendar view url, in the calendar view right clic -> copy view url
	"property":"deadline" #name of the property that holds a Date. In my case deadline, pretty straightforward
}
```
To get the tokenV2 I do explain it on my other notion repo here https://github.com/elblogbruno/NotionAI-MyMind.

This project was inspired why https://github.com/evertheylen/notion-export-ics that the idea to get it done is simpler, but this one I find it nicer and faster. 

## FAQS

```
Traceback (most recent call last):
File ".../notion/notion-export-ics/webapp.py", line 38, in make_ics
cal = get_ical(client, calendar_url, title_format)
File ".../notion/notion-export-ics/notion_ics.py", line 27, in get_ical
calendar_query = calendar_view.build_query()
File ".../notion/collection.py", line 249, in build_query
"query"
KeyError: 'query'
```

If you get this error see this:

```
jamalex/notion-py#190 I made a pull request fixing the issue. A quick one is to manually modify the notion/collection.py go to the line 249 and change "query" for "query2".
```
