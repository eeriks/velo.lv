from fabric.api import *
import os


# Local paths
LOCAL_ROOT = os.path.dirname(os.path.realpath(__file__))

# Server paths
PROJECT_NAME = "velo"
PROJECT_PATH = "/code/project"

MANAGE_BIN = "/code/project/manage.py"
VENV_PATH = "/var/lib/venv/"

@task
def makeMessages():
    project_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "project")
    dirs = os.listdir(project_root)
    for app in dirs:
        app_path = os.path.join(PROJECT_PATH, app)
        if(os.path.exists(os.path.join(project_root, app, "locale"))):
            local("cd %s; %s makemessages -a --no-wrap" % (app_path, VENV_PATH + "/bin/django-admin.py"))
            # local("cd %s; %s makemessages -a -d djangojs --no-wrap -e js,coffee" % (app_path, VENV_PATH + "/bin/django-admin.py"))

@task
def compileMessages():
    project_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "project")
    dirs = os.listdir(project_root)
    for app in dirs:
        app_path = os.path.join(PROJECT_PATH, app)
        if(os.path.exists(os.path.join(project_root, app, "locale"))):
            local("cd %s; %s compilemessages" % (app_path, VENV_PATH + "/bin/django-admin.py"))
