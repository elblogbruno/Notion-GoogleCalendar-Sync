def search_task_on_notion(calendar_entries,task_title):
    print("Searching {0} task on notion".format(task_title))
    for entry in calendar_entries:
        if entry.title == task_title:
            print("Task was found")
            return entry
    return None
