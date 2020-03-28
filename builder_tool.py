import sys
import string
from pprint import pprint
import requests
from termcolor import *

currentServer = "https://dca8234f.ngrok.io/"

cont = True

def postPath(name, message, endpoint, retain = ""):
    response = requests.post(
        currentServer+endpoint,
        data = {
        "name": name,
        "message": message,
        "retain" : retain
        }
        )
    pprint(response.json())

def postRecord(message):
    response = requests.post(
        currentServer+"recordAction",
        data = {
        "message": message
        }
        )
    pprint(response.json())

def postUpdate(name, message, endpoint, pid=""):
    response = requests.post(
        currentServer+endpoint,
        data = {
        "name": name,
        "message": message,
        "pid" : pid,
        }
        )
    pprint(response.json())

def postInfo(name):
    response = requests.post(
        currentServer+"pathInfo",
        data = {
        "name": name,
        }
        )
    pprint(response.json())

def postBuild(service):
    response = requests.post(
        currentServer+'buildIVR',
        data = {
        "service": service,
        }
        )
    pprint(response.json())

def postOption(host, message, connnectNext, endpoint):
    response = requests.post(
        currentServer+endpoint,
        data = {
        "connectHost": host,
        "message": message,

        "connectNext": connectNext
        }
        )
    pprint(response.json())

while cont:
    print(colored("Welcome to the ivrTREE builder. We hope you enjoy making great creations", "green"))
    print("1. New Host/Option, 2. Update Host/Option 3. Add Record Option 4. TODO list 5. Current Paths/Hosts 6. Current Tree 7. Build IVR")
    line = sys.stdin.readline()
    choice = line.rstrip()
    print(int(choice))
    if not int(choice) in [1,2,3,4,5,6,7]:
        cont = False
        sys.exit(0)
    elif choice == "1":
        print(colored("Enter '1' to create a path OR '2' to create a option", "green"))
        line = sys.stdin.readline()
        creationOption = line.strip()
        if creationOption == "1":
            print(colored("Enter 'name' for new path. Remember to consider connections needed", "green"))
            postPath("new","next",'noncomplete')
            line = sys.stdin.readline()
            name = line.strip()
            print(colored("Enter 'message' for new path.", "green"))
            line = sys.stdin.readline()
            message = line.strip()
            print(colored("Press 'enter' to retain: True or enter any key to retain:False", "green"))
            line = sys.stdin.readline()
            retain = line.strip()
            if retain == None:
                retain = retain
                postPath(name, message, 'newPath', retain)
                addOption = False
            else:
                postPath(name, message, 'newPath', retain)
                addOption = True
            while addOption:
                print(colored("Press '1' to add option OR Press '2' to skip", "green"))
                line = sys.stdin.readline()
                add = line.strip()
                if add == "1":
                    host = name
                    print(colored("Enter a message for this option - Press # to ...", "green"))
                    line = sys.stdin.readline()
                    message = line.strip()
                    print(colored("Please enter next connection name:", "green"))
                    line = sys.stdin.readline()
                    connectNext = line.strip()
                    postOption(host, message, connectNext, 'newOption')
                else:
                    addOption = False
        elif creationOption == "2":
            print(colored("Please select host OR create a new path/host", "green"))
            postPath("new","next", 'connections')
            line = sys.stdin.readline()
            host = line.strip()
            print(colored("Enter an message for this option - Press # to ...", "green"))  
            line = sys.stdin.readline()
            message = line.strip()
            print(colored("Please enter next connection/host name:", "green"))
            line = sys.stdin.readline()
            connectNext = line.strip()
            postOption(host, message, connectNext, 'newOption')
        else:
            print(colored("Incorrect Entry", "red"))
            continue
    elif choice == "2":
        print(colored("Enter '1' to update a path OR '2' to update a option", "green"))
        line = sys.stdin.readline()
        updateOption = line.strip()
        if updateOption == "1":
            print(colored("Enter 'name' of the path you want to update", "green"))
            postPath("new","next", 'connections')
            line = sys.stdin.readline()
            name = line.strip()
            postInfo(name)
            print(colored("Enter 'message' for new path.", "green"))
            line = sys.stdin.readline()
            message = line.strip()
            print(colored("Press 'enter' to retain: True or enter any key to retain:False", "green"))
            line = sys.stdin.readline()
            retain = line.strip()
            postUpdate(name, message, "updatePath")
        elif updateOption == "2":
            print(colored("Please select host OR create a new path/host", "green"))
            postPath("new","next", 'connections')
            line = sys.stdin.readline()
            host = line.strip()
            postInfo(host)
            print(colored("Please select the 'pid' assoicated with the option you want to change", "green"))
            line = sys.stdin.readline()
            pid = line.strip()
            print(colored("Enter an message for this option - Press # to ...", "green"))  
            line = sys.stdin.readline()
            message = line.strip()
            postUpdate(host, message, 'updateOption', pid)
        else:
            print(colored("Incorrect Entry", "red"))
            continue
    elif choice == "3":
        print(colored("Add a message EG: 'Please leave a message after the tone'", "green"))
        line = sys.stdin.readline()
        message = line.strip()
        postRecord(message)
    elif choice == "4":
        postPath("new","next",'noncomplete')
    elif choice == "5":
        postPath("new","next", 'connections')
    elif choice == "6":
        postPath("new","next", 'currentTree')
    elif choice == "7":
        print(colored("Enter 'sms', 'voice' or 'both'", "green"))  
        line = sys.stdin.readline()
        buildChoice = line.strip()
        postBuild(buildChoice) 