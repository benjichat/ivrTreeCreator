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

print()

while cont:
    print(colored("Please choose your action", "green"))
    print(colored("1. New Host/Option", "yellow"))
    print(colored("2. Update Host/Option", "yellow"))
    print(colored("3. Add Record Option", "yellow")) 
    print(colored("4. TODO list", "yellow")) 
    print(colored("5. Current Paths/Hosts", "yellow")) 
    print(colored("6. Current Tree", "yellow")) 
    print(colored("7. Build IVR", "yellow"))
    line = sys.stdin.readline()
    choice = line.rstrip()
    if not int(choice) in [1,2,3,4,5,6,7]:
        cont = False
        sys.exit(0)
    elif choice == "1":
        print(colored("Enter '1' to create a path OR '2' to create a option", "green"))
        print()
        line = sys.stdin.readline()
        creationOption = line.strip()
        if creationOption == "1":
            print(colored("Enter 'name' for new path. Remember to consider connections needed", "green"))
            current = postPath("new","next",'noncomplete')
            if current == {"todo" : "NO PATHS AVAILABLE"}:
                print(colored("NO PATHS AVAILABLE", "red"))
            else:
                for x in current["todo"]:
                    print(colored(x, "yellow"))
            print()
            line = sys.stdin.readline()
            name = line.strip()
            print(colored("Enter 'message' for new path.", "green"))
            print()
            line = sys.stdin.readline()
            message = line.strip()
            print(colored("Press 'enter' to retain: True or enter any key to retain:False", "green"))
            print()
            line = sys.stdin.readline()
            retain = line.strip()
            if retain == None:
                retain = retain
                current = postPath(name, message, 'newPath', retain)
                print(colored(current, "cyan"))
                print()
                addOption = False
            else:
                current = postPath(name, message, 'newPath', retain)
                print(colored(current, "cyan"))
                print()
                addOption = True
            while addOption:
                print(colored("Press '1' to add option OR Press '2' to skip", "green"))
                print()
                line = sys.stdin.readline()
                add = line.strip()
                if add == "1":
                    host = name
                    print(colored("Enter a message for this option - Press # to ...", "green"))
                    print()
                    line = sys.stdin.readline()
                    message = line.strip()
                    print(colored("Please enter next connection name:", "green"))
                    print()
                    line = sys.stdin.readline()
                    connectNext = line.strip()
                    current = postOption(host, message, connectNext, 'newOption')
                    print(colored(current, "cyan"))
                    print()
                else:
                    addOption = False
        elif creationOption == "2":
            print(colored("Please select host OR create a new path/host", "green"))
            current = postPath("new","next", 'connections')
            for path in current["list of paths"]:
                print(colored(path["name"], "yellow"))
            print()
            line = sys.stdin.readline()
            host = line.strip()
            print(colored("Enter an message for this option - Press # to ...", "green"))  
            print()
            line = sys.stdin.readline()
            message = line.strip()
            print(colored("Please enter next connection/host name:", "green"))
            print()
            line = sys.stdin.readline()
            connectNext = line.strip()
            current = postOption(host, message, connectNext, 'newOption')
            print(colored(current, "cyan"))
            print()
        else:
            print(colored("Incorrect Entry", "red"))
            continue
    elif choice == "2":
        print(colored("Enter '1' to update a path OR '2' to update a option", "green"))
        print()
        line = sys.stdin.readline()
        updateOption = line.strip()
        if updateOption == "1":
            print(colored("Enter 'name' of the path you want to update", "green"))
            current = postPath("new","next", 'connections')
            for path in current["list of paths"]:
                print(colored(path["name"], "yellow"))
            print()
            line = sys.stdin.readline()
            name = line.strip()
            current = postInfo(name)
            if current["info"] == "NO PATH FOUND":
                print(colored("NO PATH FOUND", "red"))
            else:
                print(colored(current, "yellow"))
            print(colored("Enter 'message' for new path.", "green"))
            print()
            line = sys.stdin.readline()
            message = line.strip()
            print(colored("Press 'enter' to retain: True or enter any key to retain:False", "green"))
            print()
            line = sys.stdin.readline()
            retain = line.strip()
            current = postUpdate(name, message, "updatePath")
            print(colored(current, "cyan"))
            print()
        elif updateOption == "2":
            print(colored("Please select host OR create a new path/host", "green"))
            current = postPath("new","next", 'connections')
            for path in current["list of paths"]:
                print(colored(path["name"], "yellow"))
            print()
            line = sys.stdin.readline()
            host = line.strip()
            current = postInfo(host, options = True)
            if current["info"] == "NO PATH FOUND":
                print(colored("NO PATH FOUND", "red"))
            else:
                for x in current["info"]["options"]:
                    print(colored(x, "yellow"))
            print(colored("Please select the 'pid' assoicated with the option you want to change", "green"))
            print()
            line = sys.stdin.readline()
            pid = line.strip()
            print(colored("Enter an message for this option - Press # to ...", "green"))  
            line = sys.stdin.readline()
            message = line.strip()
            current = postUpdate(host, message, 'updateOption', pid)
            print(colored(current, "cyan"))
            print()
        else:
            print(colored("Incorrect Entry", "red"))
            print()
            continue
    elif choice == "3":
        print(colored("Add a message EG: 'Please leave a message after the tone'", "green"))
        line = sys.stdin.readline()
        message = line.strip()
        current = postRecord(message)
        print(colored(current, "cyan"))
        print()
    elif choice == "4":
        print(colored("List of connections with no associated host paths:", "green"))
        current = postPath("new","next",'noncomplete')
        if current["todo"] == "NO PATHS AVAILABLE":
                print(colored("NO PATHS AVAILABLE", "red"))
        else:
            for x in current["todo"]:
                print(colored("- " + x, "yellow"))
        print()
    elif choice == "5":
        print(colored("List of current host paths:", "green"))
        current = postPath("new","next", 'connections')
        if current["list of paths"] == "NO PATHS AVAILABLE":
            print(colored("NO PATHS AVAILABLE", "red"))
        else:
            for x in current["list of paths"]:
                print(colored(x, "yellow"))
        print()
    elif choice == "6":
        print(colored("Press '1' for formatted or '2' for raw JSON", "green"))
        line = sys.stdin.readline()
        choice = line.strip()
        current = postPath("new","next", 'currentTree')
        if int(choice) == 1:
            for x in current:
                print(colored("HOST: " + x["name"], "cyan"))
                print(colored("MESSAGE: " + x["message"], "yellow"))
                if "options" in x:
                    for option in x["options"]:
                        print(colored("       OPTION: " + str(option["pid"]) + ". " + option["connection"], "magenta"))
                        print(colored("       MESSAGE: " + option["message"], "blue"))
        else:
            print(current)
        print()
    elif choice == "7":
        print(colored("Please select what form of IVR Tree you would like to build", "green"))
        print(colored("'sms', 'voice' or 'both'", "yellow"))  
        line = sys.stdin.readline()
        buildChoice = line.strip()
        current = postBuild(buildChoice)
        print(colored(current, "cyan"))
        print()