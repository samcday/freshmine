import os
import pytz
import redmine
import re
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


def build_projects_lookup():
    '''Builds lookup table of Redmine project IDs to Freshbook project IDs.'''
    for project in freshbooks_client.project.list().projects.project:
        m = redmine_id_regex.match(str(project.description))
        if m:
            project_lookup[m.group(1)] = project.project_id


def freshbooks_project(redmine_project):
    '''Finds or creates a FreshBooks project for a corresponding Redmine one'''
    

def redmine_time_entries_since(user_id, date):
    for entry in redmine.time_entries:
        if entry.created_on < date:
            return
        if entry.user.id == user_id:
            yield entry


build_projects_lookup()
print(project_lookup)

# since = datetime.datetime(2013, 5, 20, tzinfo=timezone)
# for entry in redmine_time_entries_since(my_redmine_user_id, since):
#     print(entry.comments)
