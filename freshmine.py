import os
import pytz
import redmine
import re
import datetime
from refreshbooks import api as refreshbooks

my_redmine_user_id = 22
timezone = pytz.timezone("Australia/Brisbane")

redmine_url = os.environ["REDMINE_URL"]
redmine_key = os.environ["REDMINE_KEY"]
redmine_client = redmine.Redmine(redmine_url, key=redmine_key, version=1.4)

freshbooks_host = os.environ["FRESHBOOKS_HOST"]
freshbooks_key = os.environ["FRESHBOOKS_KEY"]
freshbooks_client = refreshbooks.TokenClient(freshbooks_host, freshbooks_key)

redmine_id_regex = re.compile("^Redmine ID: (\d+)$")

project_lookup = dict()
task_lookup = dict()
time_entry_lookup = dict()


def build_projects_lookup():
    '''Builds lookup table of Redmine project IDs to Freshbooks project IDs.'''
    resp = freshbooks_client.project.list()
    if not len(resp.projects):
        return
    for project in resp.projects.project:
        m = redmine_id_regex.match(str(project.description))
        if m:
            project_lookup[int(m.group(1))] = project.project_id


def build_tasks_lookup():
    '''Builds lookup table for task names to Freshbooks task ids.'''
    for task in freshbooks_client.task.list().tasks.task:
        task_lookup[task.name] = task.task_id


def freshbooks_task(task_name):
    freshbooks_id = task_lookup.get(task_name)
    if freshbooks_id is not None:
        return freshbooks_id
    freshbooks_id = freshbooks_client.task.create(
        name=task_name,
        billable=1
    ).task_id
    task_lookup[task_name] = freshbooks_id
    return freshbooks_id


def freshbooks_project(redmine_project):
    '''Finds or creates a FreshBooks project for a corresponding Redmine one'''
    freshbooks_id = project_lookup.get(redmine_project.id)
    if freshbooks_id is not None:
        return freshbooks_id
    freshbooks_id = freshbooks_client.project.create(
        project={
            "name": redmine_project.name,
            "client_id": 2,
            "bill_method": "staff-rate",
            "description": "Redmine ID: %d" % redmine_project.id,
            "tasks": [
                refreshbooks.types.task(task_id=1)
            ]
        }
    ).project_id
    print("Created project {0} in Freshbooks. ID: {1}".format(
        redmine_project.name, freshbooks_id))
    project_lookup[redmine_project.id] = freshbooks_id
    return freshbooks_id


def build_time_entry_lookup(project_id):
    time_entry_lookup[project_id] = list()
    resp = freshbooks_client.time_entry.list(project_id=project_id)
    if not len(resp.time_entries):
        return time_entry_lookup[project_id]
    for entry in resp.time_entries.time_entry:
        m = redmine_id_regex.match(str(entry.notes))
        if m:
            time_entry_lookup[project_id].append(int(m.group(1)))
    return time_entry_lookup[project_id]


def sync_time_entry(redmine_entry):
    project_id = freshbooks_project(redmine_entry.project)
    time_entries = time_entry_lookup.get(project_id)
    if time_entries is None:
        time_entries = build_time_entry_lookup(project_id)
    if redmine_entry.id in time_entries:
        return
    freshbooks_client.time_entry.create(
        time_entry={
            "project_id": project_id,
            "task_id": "1",
            "staff_id": "1",
            "hours": redmine_entry.hours,
            "notes": "Redmine ID: %d" % redmine_entry.id,
            "date": str(redmine_entry.spent_on)
        }
    )
    print("Synced new time entry on {0} for {1} hours"
          .format(redmine_entry.spent_on, redmine_entry.hours))


def redmine_time_entries_since(user_id, date):
    for entry in redmine_client.time_entries:
        if entry.created_on < date:
            return
        if entry.user.id == user_id:
            yield entry


build_projects_lookup()
build_tasks_lookup()

since = datetime.datetime(2013, 5, 20, tzinfo=timezone)
for entry in redmine_time_entries_since(my_redmine_user_id, since):
    sync_time_entry(entry)
