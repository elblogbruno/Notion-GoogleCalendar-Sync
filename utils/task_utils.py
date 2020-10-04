from datetime import date
from gtasks import Gtasks

def search_task(gt,task_list_id,task_title,due_date,completion_date):
    tasks = gt.get_tasks(task_list=task_list_id, due_min=due_date, due_max=completion_date)
    for task in tasks:
        if task_title in task.title:
            return task
    return None

def add_task_to_list(gt,task_list_id,task_title,due_date,completion_date,description):
    task = search_task(gt,task_list_id,task_title,due_date,completion_date)
    if task == None:
        print("Adding task to list")
        current_list = gt.get_list(task_list_id)
        current_list.new_task(task_title,due_date=due_date,completion_date=completion_date,notes=description)
    else:
        print("Task does exists already")
    
def remove_task_from_list(gt,task_list_id,task_title,due_date,completion_date):
    task = search_task(gt,task_list_id,task_title,due_date,completion_date)
    if task != None:
        task.complete = True
            
def list_available_lists():
    gt = Gtasks()
    available_list = gt.get_lists()

    list_names = []
    list_index = 0

    i = 1
    if len(available_list) > 1:
        print("These are your avaliable task list, please choose one: ")
        for task_list in available_list:
            print("{0}) {1}".format(i,task_list))
            list_names.append(task_list)
            i=i+1
        list_index = input("Choose a list by the number: ")

        while int(list_index) < 0 or int(list_index) > len(list_names):
            print(list_index)
            print("Choose a playlist available on the list.")
            list_index = input("Choose a playlist by the number: ")

        print ("Gonna syncronize notion tasks with this task list {0}".format(list_names[int(list_index)-1]))
        
        
    else:
        print("There is only one list available, so don't need to choose.")
        list_names.append(available_list[0])
        list_index = 0
       
    final_id = list_names[int(list_index)-1]
    return str(final_id)

if __name__ == "__main__":
    name = list_available_lists()    
    print(name)