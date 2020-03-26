import sys
import string
from pprint import pprint
import requests

cont = True

def postPath(name, message, endpoint, retain = ""):
    response = requests.post(
        'https://dca8234f.ngrok.io/'+endpoint,
        data = {
        "name": name,
        "message": message,
        "retain" : retain
        }
        )
    pprint(response.json())

def postOption(host, message, connnectNext, endpoint):
    response = requests.post(
        'https://dca8234f.ngrok.io/'+endpoint,
        data = {
        "connectHost": host,
        "message": message,

        "connectNext": connectNext
        }
        )
    pprint(response.text)

while cont:
    print("1. New Path, 2. New Options, 3. TODO list, 4. Current options, 5. Current Tree, 6. Build IVR")
    line = sys.stdin.readline()
    choice = line.rstrip()

    if not int(choice) != [1,2,3,4]:
        cont = False
        sys.exit(0)
    elif choice == "1":
        print("Enter 'name' for new path. Remember to consider connections needed")
        postPath("new","next",'noncomplete')
        line = sys.stdin.readline()
        name = line.strip()
        print("Enter 'message' for new path.")
        line = sys.stdin.readline()
        message = line.strip()
        print("Press 'enter' to retain: True or enter any key to retain:False")
        line = sys.stdin.readline()
        retain = line.strip()
        if retain == None:
            retain = retain
            postPath(name, message, 'newPath', retain)
            addOption = True
        else:
            postPath(name, message, 'newPath', retain)
            addOption = False
        while addOption:
            print("Press '1' to add option OR Press '2' to skip")
            line = sys.stdin.readline()
            add = line.strip()
            if add == "1":
                host = name
                print("Please enter option messaage (without any numbering)")
                line = sys.stdin.readline()
                message = line.strip()
                print("Please enter next connection name:")
                line = sys.stdin.readline()
                connectNext = line.strip()
                postOption(host, message, connectNext, 'newOption')
            else:
                addOption = False
    elif choice == "2":
        print("Please select host:")
        postPath("new","next", 'connections')
        line = sys.stdin.readline()
        host = line.strip()
        print("Please enter message:")  
        line = sys.stdin.readline()
        message = line.strip()
        print("Please enter next connection name:")
        line = sys.stdin.readline()
        connectNext = line.strip()
        postOption(host, message, connectNext, 'newOption')
    elif choice == "3":
        postPath("new","next",'noncomplete')
    elif choice == "4":
        postPath("new","next", 'connections')
    elif choice == "5":
        postPath("new","next", 'currentTree')
    elif choice == "6":
        postPath("new", "next", 'buildIVR') 