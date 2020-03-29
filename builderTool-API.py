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
    response = response.json()
    return response

def postOption(host, message, connnectNext, endpoint):
    response = requests.post(
        currentServer+endpoint,
        data = {
        "connectHost": host,
        "message": message,

        "connectNext": connectNext
        }
        )
    response = response.json()
    return response

def postRecord(message):
    response = requests.post(
        currentServer+"recordAction",
        data = {
        "message": message
        }
        )
    response = response.json()
    return response

def postUpdate(name, message, endpoint, pid=""):
    response = requests.post(
        currentServer+endpoint,
        data = {
        "name": name,
        "message": message,
        "pid" : pid,
        }
        )
    response = response.json()
    return response

def postInfo(name, options = False):
    response = requests.post(
        currentServer+"pathInfo",
        data = {
        "name": name,
        "options": options
        }
        )
    response = response.json()
    return response

def postBuild(service):
    response = requests.post(
        currentServer+'buildIVR',
        data = {
        "service": service,
        }
        )
    response = response.json()
    return response



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
            current = postPath("new","next",'noncomplete')
            for x in current["todo"]:
                print(colored(x, "yellow"))
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
                current = postPath(name, message, 'newPath', retain)
                print(colored(current, "cyan"))
                addOption = False
            else:
                current = postPath(name, message, 'newPath', retain)
                print(colored(current, "cyan"))
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
                    current = postOption(host, message, connectNext, 'newOption')
                    print(colored(current, "cyan"))
                else:
                    addOption = False
        elif creationOption == "2":
            print(colored("Please select host OR create a new path/host", "green"))
            current = postPath("new","next", 'connections')
            for path in current["list of paths"]:
                print(colored(path["name"], "yellow"))
            line = sys.stdin.readline()
            host = line.strip()
            print(colored("Enter an message for this option - Press # to ...", "green"))  
            line = sys.stdin.readline()
            message = line.strip()
            print(colored("Please enter next connection/host name:", "green"))
            line = sys.stdin.readline()
            connectNext = line.strip()
            current = postOption(host, message, connectNext, 'newOption')
            print(colored(current, "cyan"))
        else:
            print(colored("Incorrect Entry", "red"))
            continue
    elif choice == "2":
        print(colored("Enter '1' to update a path OR '2' to update a option", "green"))
        line = sys.stdin.readline()
        updateOption = line.strip()
        if updateOption == "1":
            print(colored("Enter 'name' of the path you want to update", "green"))
            current = postPath("new","next", 'connections')
            for path in current["list of paths"]:
                print(colored(path["name"], "yellow"))
            line = sys.stdin.readline()
            name = line.strip()
            current = postInfo(name)
            if current["info"] == "NO PATH FOUND":
                print(colored("NO PATH FOUND", "red"))
            else:
                print(colored(current, "yellow"))
            print(colored("Enter 'message' for new path.", "green"))
            line = sys.stdin.readline()
            message = line.strip()
            print(colored("Press 'enter' to retain: True or enter any key to retain:False", "green"))
            line = sys.stdin.readline()
            retain = line.strip()
            current = postUpdate(name, message, "updatePath")
            print(colored(current, "cyan"))
        elif updateOption == "2":
            print(colored("Please select host OR create a new path/host", "green"))
            current = postPath("new","next", 'connections')
            for path in current["list of paths"]:
                print(colored(path["name"], "yellow"))
            line = sys.stdin.readline()
            host = line.strip()
            current = postInfo(host, options = True)
            if current["info"] == "NO PATH FOUND":
                print(colored("NO PATH FOUND", "red"))
            else:
                for x in current["info"]["options"]:
                    print(colored(x, "yellow"))
            print(colored("Please select the 'pid' assoicated with the option you want to change", "green"))
            line = sys.stdin.readline()
            pid = line.strip()
            print(colored("Enter an message for this option - Press # to ...", "green"))  
            line = sys.stdin.readline()
            message = line.strip()
            current = postUpdate(host, message, 'updateOption', pid)
            print(colored(current, "cyan"))
        else:
            print(colored("Incorrect Entry", "red"))
            continue
    elif choice == "3":
        print(colored("Add a message EG: 'Please leave a message after the tone'", "green"))
        line = sys.stdin.readline()
        message = line.strip()
        current = postRecord(message)
        print(colored(current, "cyan"))
    elif choice == "4":
        current = postPath("new","next",'noncomplete')
        for x in current["todo"]:
            print(colored(x, "yellow"))
    elif choice == "5":
        current = postPath("new","next", 'connections')
        for path in current["list of paths"]:
            print(colored(path["name"], "yellow"))
    elif choice == "6":
        current = postPath("new","next", 'currentTree')
        for x in current:
            print(colored("HOST: " + x["name"], "cyan"))
            print(colored("MESSAGE: " + x["message"], "yellow"))
            if "options" in x:
                for option in x["options"]:
                    print(colored("       OPTION: " + str(option["pid"]) + ". " + option["connection"], "magenta"))
                    print(colored("       MESSAGE: " + option["message"], "blue"))
    elif choice == "7":
        print(colored("Enter 'sms', 'voice' or 'both'", "green"))  
        line = sys.stdin.readline()
        buildChoice = line.strip()
        current = postBuild(buildChoice)
        print(colored(current, "cyan"))