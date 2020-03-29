from pprint import pprint
import config
import json
import urllib
import requests
from test_start import *
from pymongo import MongoClient
from bottle import request, post, run, get, route, response
from createVoice import createSSML
from bson import json_util #https://stackoverflow.com/questions/19674311/json-serializing-mongodb

client = MongoClient("mongodb+srv://"+config.mongo_user+":"+config.mongo_pass+"@troll-demo-v0dyx.mongodb.net/test?retryWrites=true&w=majority")
db = client.get_database("creator")
currentCollection = db.daniel #usecase database
collectionName = "daniel"
currentServer = "https://dca8234f.ngrok.io/"

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
        if currentCollection.find_one({"name":self.name}):
            print("already path with this name")
            return {"error":"There is already a path with this name. Check your current paths by posting to /pathState"}
        pid = len(list(currentCollection.aggregate([{"$sort":{"pid":1}}])))
        if pid == 0:
            pid = 1
        else:
            pid += 1
        newPath = {"name":self.name, "pid":pid, "message":self.message,"options":[], "retain": self.retain}
        currentCollection.insert_one(newPath)
        print("Adding new connection")
        return {"name":self.name, "pid":pid, "message":self.message}

    def newRecord(self):
        if currentCollection.find_one({"name":self.name}):
            print("already path with this name")
            return {"error":"There is already a path with this name. Check your current paths by posting to /pathState"}
        pid = len(list(currentCollection.aggregate([{"$sort":{"pid":1}}])))
        if pid == 0:
            pid = 1
        else:
            pid += 1
        newPath = {"name":self.name, "pid":pid, "message":self.message, "retain": self.retain}
        currentCollection.insert_one(newPath)
        print("Adding new connection")
        return {"name":self.name, "pid":pid, "message":self.message}

class optionCreator:
    def __init__(self, connectHost, connectNext, message):
        self.connectHost = connectHost
        self.connectNext = connectNext
        self.message = message

    def newOption(self):
        currentConnection = currentCollection.find_one({"name":self.connectHost})
        if currentConnection:
            for option in currentConnection["options"]:
                if option["connection"] == self.connectNext:
                    print("This 'next connection' already exists")
                    return {"error":"This 'next connection' already exists"}
            pid = len(list(currentConnection["options"]))
            if pid == 0:
                pid = 1
            else:
                pid += 1
            self.newOption = {"pid":pid, "connection": self.connectNext, "message":self.message}
            currentCollection.update_one(currentConnection,{"$push":{"options":self.newOption}})
            currentConnection = currentCollection.find_one({"name":self.connectHost})
            return {"success":"new option added"}
        else:
            return {"error":"could not find a host with this name"}

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
    return entry.newPath()

@post('/recordAction')
def newPath():
    print("-------------------- NEW PATH POST-------------------------------")
    name = "record"
    message = request.forms.get("message")
    print(message)
    entry = pathCreator(name, message, retain=False)
    return entry.newRecord()

@post('/newOption')
def newOption():
    print("-------------------- NEW OPTION POST-------------------------------")
    connectHost = request.forms.get("connectHost")
    connectNext= request.forms.get("connectNext")
    message= request.forms.get("message")
    entry = optionCreator(connectHost, connectNext, message)
    newOption = entry.newOption()
    return newOption

def editPathMessage(name, message, pid=""):
    editPath = currentCollection.find_one({"name":name})
    if not editPath:
        print("no path with this name")
        return {"error":"There is no path with this name"}
    else:
        if pid != "":
            currentCollection.update_one(editPath,{"$set":{"options.$[el1].message":message}}, array_filters=[{"el1.pid":int(pid)}])
        else:
            currentCollection.update_one(editPath,{"$set":{"message":message}})
    editPath = currentCollection.find_one({"name":name})
    return {"updated" : {"name":editPath["name"],"message":editPath["message"], "options":editPath["options"]}}

@post('/updatePath')
def update():
    name = request.forms.get("name")
    message= request.forms.get("message")
    return editPathMessage(name, message)

@post('/updateOption')
def update():
    name = request.forms.get("name")
    pid = request.forms.get("pid")
    message= request.forms.get("message")
    return editPathMessage(name, message, pid=pid)

@post('/pathInfo')
def getInfo():
    name = request.forms.get("name")
    options = request.forms.get("options")
    print(name)
    info = currentCollection.find_one({"name":name})
    if options:
        info = {"info":{"name":info["name"], "options": info["options"]}}
    else:
        info = {"info":{"name":info["name"], "message":info["message"], "options":len(info["options"])}}
    if info:
        return info
        #return json.dumps(info["name"],default=json_util.default)
    else:
        return {"info":"NO PATH FOUND"}


#This section builds the voice responses for for thosts (https://cloud.google.com/text-to-speech/docs)

def buildIVR(service):
    allRows = currentCollection.find({})
    builtTree = {"branches built":[]}
    if not service in ["sms", "voice", "both"]:
        return {"error":"Please choose 'sms', 'voice' or 'both'"}
    for row in allRows:
        smsMessage = row["message"]
        voiceMessage = row["message"]
        if row["name"] == "record":
            voiceUpdate = createSSML(str(voiceMessage))
            voiceIVR = {"play":voiceUpdate, "digits":1, "timeout": 4, "skippable":True, "next": {"play":currentServer+"static/tone.wav", "next":{"record":currentServer+"recordings"}}}
            currentCollection.update_one(row,{"$set":{"voiceIVR":voiceIVR}})
        else:
            for option in row["options"]:
                voiceMessage += "<break time='1' /> Press " + str(option["pid"]) + " to " + option["message"]
                smsMessage += "\r\n" + str(option["pid"]) + ". " +   option["message"]
            print("--------------------- BUILDING IVR TREE -------------------------------")
            if service == "voice":
                voiceUpdate = createSSML(str(voiceMessage))
                voiceIVR = {"ivr":voiceUpdate, "digits":1, "timeout": 4, "skippable":True, "next": currentServer +"voiceCont"}
                currentCollection.update_one(row,{"$set":{"voiceIVR":voiceIVR}})
            elif service == "both":
                voiceUpdate = createSSML(str(voiceMessage))
                voiceIVR = {"ivr":voiceUpdate, "digits":1, "timeout": 4, "skippable":True, "next": currentServer +"voiceCont"}
                currentCollection.update_one(row,{"$set":{"voiceIVR":voiceIVR, "smsIVR":smsMessage}})
            else:
                currentCollection.update_one(row,{"$set":{"smsIVR":smsMessage}})
        builtTree["branches built"].append({"name":row["name"], "pid":row["pid"]})
    if builtTree["branches built"] == []:
        return {"branches built":"no tree to build, please add new paths and options"}
    else:
        return builtTree

@post('/buildIVR')
def build_IVR():
    service = request.forms.get("service")
    print(service)
    return buildIVR(service)

# This section defines non-complete sections. Sections that have been called as options but no host path

def nonCompletePaths():
    print("---------------------NON COMPLETE PATHS-------------------------------")
    list_of_connections = []
    non_complete = {"todo":[]}
    allRows = currentCollection.find({})
    #print(sorted_list)
    for x in allRows:
        if 'options' in x:
            for option in x["options"]:
                list_of_connections.append(option["connection"])
    for x in list_of_connections:
        if not currentCollection.find_one({"name":x}):
            non_complete["todo"].append(x)
            print(x)
    if non_complete["todo"] == []:
        return {"todo" : "NO PATHS AVAILABLE"}
    else:
        return non_complete

@post('/noncomplete')
def noncomplete():
    response.content_type = 'application/json'
    return nonCompletePaths()

#This is defining the optional host questions

def optionalConnections():
    print("---------------------CONNECTIONS AVAILABLE-------------------------------")
    allRows = currentCollection.find({})
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
    fetch_list = list(currentCollection.aggregate([{"$sort":{"pid":1}}]))
    pathState = {"state":[]}
    for row in fetch_list:
        rowAdd = {"name":row["name"], "message":row["message"], "retain":row["retain"]  ,"options":row["options"]}
        pathState["state"].append(rowAdd)
    return pathState

@post('/currentTree')
def connections():
    #response.content_type = 'application/json'
    current = list(currentCollection.aggregate([{"$sort":{"pid":1}}]))
    return json.dumps(current,default=json_util.default)
    #return pathState()



#This allows users to test the konversationsAPI useability

@post('/test')
def test():
    testNumber = str(request.forms.get("testNumber"))
    start = currentCollection.find_one({"pid":1})
    startMessage = start["message"]
    print(testNumber, startMessage)
    response = requests.post(
    'https://api.46elks.com/a1/conversations',
    auth = (config.elks_user, config.elks_pass),
    data = {
            "to": testNumber,
            "message": startMessage,
            "token": "new1234567",
            "reply_url": currentServer+"test_response"
            },
    )
    print(response)

run(host='0.0.0.0', port=5501)