from pprint import pprint
import config
import json
import urllib
import requests
from test_start import *
from pymongo import MongoClient
from bottle import request, post, run, get, route, response
from createVoice import createVoice, createSSML

client = MongoClient("mongodb+srv://"+config.mongo_user+":"+config.mongo_pass+"@troll-demo-v0dyx.mongodb.net/test?retryWrites=true&w=majority")
db = client.get_database("creator")
first = db.third#usecase database
collectionName = "third"

print()
print()
print("BOOTING BUILDER API FOR COLLECTION '" + collectionName + "'")
print()
print()

class pathCreator:
    def __init__(self, name, message, retain = True):
        self.name = name
        self.message = message
        self.retain = retain
    
    def newPath(self):
        if first.find_one({"name":self.name}):
            print("already path with this name")
            return "There is already a path with this name. Check your current paths by posting to /pathState"
        pid = len(list(first.aggregate([{"$sort":{"pid":1}}])))
        if pid == 0:
            pid = 1
        else:
            pid += 1
        textVoice = createVoice(str(self.message))
        newPath = {"name":self.name, "pid":pid, "message":self.message,"options":[], "retain": self.retain, "voice":textVoice}
        first.insert_one(newPath)
        print("Adding new connection")
        return {"name":self.name, "pid":pid, "message":self.message}

class optionCreator:
    def __init__(self, connectHost, connectNext, message):
        self.connectHost = connectHost
        self.connectNext = connectNext
        self.message = message

    def newOption(self):
        currentConnection = first.find_one({"name":self.connectHost})
        if currentConnection:
            for option in currentConnection["options"]:
                if option["connection"] == self.connectNext:
                    print("This 'next connection' already exists")
                    return "This 'next connection' already exists"
            pid = len(list(currentConnection["options"]))
            if pid == 0:
                pid = 1
            else:
                pid += 1
            self.newOption = {"pid":pid, "connection": self.connectNext, "message":self.message}
            first.update_one(currentConnection,{"$push":{"options":self.newOption}})
            currentConnection = first.find_one({"name":self.connectHost})
            return "New Option Added"
        else:
            return "Could not find path host with this name"

@post('/newPath')
def newPath():
    print("-------------------- NEW PATH POST-------------------------------")
    name = request.forms.get("name")
    message = request.forms.get("message")
    retain = bool(request.forms.get("retain"))
    if retain:
        entry = pathCreator(name, message, retain=False)
    else:
        entry = pathCreator(name, message, retain=True)
    newPath = entry.newPath()
    return newPath

@post('/newOption')
def newOption():
    print("-------------------- NEW OPTION POST-------------------------------")
    connectHost = request.forms.get("connectHost")
    connectNext= request.forms.get("connectNext")
    message= request.forms.get("message")
    entry = optionCreator(connectHost, connectNext, message)
    newOption = entry.newOption()
    return newOption

#This section builds the voice responses for for thosts (https://cloud.google.com/text-to-speech/docs)

def buildIVR():
    allRows = first.find({})
    list_of_connections = []
    non_complete = {"todo":[]}
    allRows = first.find({})
    #print(sorted_list)
    for row in allRows:
        if "voiceIVR" in row:
            continue
        else:
            voiceMessage = row["message"]
            for option in row["options"]:
                voiceMessage += "<break time='2' /> Press " + str(option["pid"]) + " for " + option["message"]
            print("--------------------- BUILDING IVR TREE -------------------------------")
            print(voiceMessage)
            voiceUpdate = createSSML(str(voiceMessage))
            voiceIVR = {"ivr":voiceUpdate, "digits":1, "timeout": 4, "skippable":True, "next":"https://dca8234f.ngrok.io/voiceCont"}
            first.update_one(row,{"$set":{"voiceIVR":voiceIVR}})

@post('/buildIVR')
def build_IVR():
    buildIVR()
    return {"state":"Done"}

# This section defines non-complete sections. Sections that have been called as options but no host path

def nonCompletePaths():
    print("---------------------NON COMPLETE PATHS-------------------------------")
    list_of_connections = []
    non_complete = {"todo":[]}
    allRows = first.find({})
    #print(sorted_list)
    for x in allRows:
        for option in x["options"]:
            list_of_connections.append(option["connection"])
    for x in list_of_connections:
        if not first.find_one({"name":x}):
            non_complete["todo"].append(x)
            print(x)
    if non_complete["todo"] == []:
        return {"paths" : "NO PATHS AVAILABLE"}
    else:
        return non_complete

@post('/noncomplete')
def noncomplete():
    response.content_type = 'application/json'
    return nonCompletePaths()

#This is defining the optional host questions

def optionalConnections():
    print("---------------------CONNECTIONS AVAILABLE-------------------------------")
    allRows = first.find({})
    connections = {"list of paths":[]}
    for x in allRows:
        connections["list of paths"].append({"name":x["name"]})
    return connections

@post('/connections')
def connections():
    response.content_type = 'application/json'
    return optionalConnections()

#This section shows the simplified version of the entire tree structure

def pathState():
    print("---------------------CURRENT STATE-------------------------------")
    fetch_list = list(first.aggregate([{"$sort":{"pid":1}}]))
    pathState = {"state":[]}
    for row in fetch_list:
        rowAdd = {"name":row["name"], "message":row["message"], "retain":row["retain"]  ,"options":row["options"]}
        pathState["state"].append(rowAdd)
    return pathState

@post('/currentTree')
def connections():
    response.content_type = 'application/json'
    return pathState()

#This allows users to test the konversationsAPI useability

@post('/test')
def test():
    testNumber = str(request.forms.get("testNumber"))
    start = first.find_one({"pid":1})
    startMessage = start["message"]
    print(testNumber, startMessage)
    response = requests.post(
    'https://api.46elks.com/a1/conversations',
    auth = (config.elks_user, config.elks_pass),
    data = {
            "to": testNumber,
            "message": message,
            "token":"new1234567",
            "reply_url": "https://dca8234f.ngrok.io/test_response"
            },
    )
    print(response)

run(host='0.0.0.0', port=5501)