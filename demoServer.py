from pprint import pprint
from bottle import request, post, run, get, route, response, static_file
import time
import string
import random
import requests
import json
import config #Create file configKonversations.py and add mongoDB username and password
from pymongo import MongoClient

client = MongoClient("mongodb+srv://"+config.mongo_user+":"+config.mongo_pass+"@troll-demo-v0dyx.mongodb.net/test?retryWrites=true&w=majority")
db = client.get_database("creator")
customers = db.customers #customer konversation database
currentCollection = db.covid #usecase database
collectionName = "covid"
currentServer = "https://dca8234f.ngrok.io/"

print()
print("BOOTING DEMO FOR COLLECTION '" + collectionName + "'")
print()

def check_new_customer(from_sender, message, created, token="sms"):
    if token == "sms":
        current_customer = customers.find_one({"mobilenumber":from_sender})
    else:
        current_customer = customers.find_one({"token":token})
    print("---------------------------- CHECKING KUND ---------------------------")
    pprint(current_customer)
    if not current_customer:
        new_customer_entry = {"mobilenumber":from_sender, "token":token, "message":message, "created":created, "request_ids":[1], "request_responses":[]}
        customers.insert_one(new_customer_entry)
        current_customer = customers.find_one({"token":token})
        print("---------------------------- NEW CUSTOMER ---------------------------")
        print("new customer added")
    print("customer already in konversation")
    return current_customer

def check_stop(message):
    print("---------------------------- CHECKING STOP ---------------------------")
    if message in ["no","stop", "opt out", "out"]:
        print("---------------------------- STOPPING ---------------------------")
        stop_message = {
            "reply":"You have been removed from our contact lists. If you change your mind you can find out more at 46elks.com",
            "retain": False,
            }
        print("Message stopping")
        return stop_message
    print("No stop message, continuing")

def check_valid_response(message,current_customer):
    current_usecase = currentCollection.find_one({"pid":current_customer["request_ids"][-1]})
    print("---------------------------- CURRENT KUND ---------------------------")
    pprint(current_customer)
    print("---------------------------- CURRENT USE ---------------------------")
    pprint(current_usecase)
    if current_usecase == None:
        print("---------------------------- DICTIONARY ERROR ---------------------------")
        print("Please check the usecase dictionary for ", current_customer["request_ids"][-1])
        print("---------------------------- DICTIONARY ERROR ---------------------------")
        availableOptions = str(len(current_usecase["options"]))
        responseMessage = "Please respond with "
        responseCounter = 1
        for i in range(availableOptions):
            responseMessage += str(responseCounter)+", "
            responseCounter += 1
        response = responseMessage
        retain = True
        return response, retain
    else:
        print("Response approved: Returning response")
        responseFind = current_usecase["options"][int(message)-1]["connection"]
        print(responseFind)
        responseFind = currentCollection.find_one({"name": responseFind})
        response, retain = responseFind["smsIVR"], responseFind["retain"]
        customers.update_one(current_customer,{"$push":{"request_responses":message, "request_ids":responseFind["pid"]}})
    return response, retain

@post('/smsStart')
def sms_usecase():
    print("---------------------------- MAIN SMS REceived -----------------------------")
    token = request.forms.get("token")
    if token == None:
        token = "sms"
    from_sender = request.forms.get("from")
    message = request.forms.get("message")
    created = request.forms.get("created")
    message = message.lower()
    if message[-1] == ".":
        message = message[:-1]
    #processing steps below   
    # check if message contains stop requests (1)
    stop_message = check_stop(message)
    if stop_message:
        return stop_message
    # checking customer pool  (2)
    current_customer = check_new_customer(from_sender, message, created, token)
    # checking incoming customer response and preparing outgoing response (3)
    response, retain = check_valid_response(message,current_customer)
    # sending outgoing response (4)
    send_response = {"reply":response, "retain":retain}
    if token == "sms":
        return {"reply":response}
    else:
        return send_response

def checkCustomerVoice(callID, from_sender, created):
    current_customer = customers.find_one({"callID":callID})
    print("---------------------------- CHECKING KUND ---------------------------")
    pprint(current_customer)
    if not current_customer:
        new_customer_entry = {"mobilenumber":from_sender, "callID":callID, "created":created, "request_ids":[1], "request_responses":[]}
        customers.insert_one(new_customer_entry)
        current_customer = customers.find_one({"callID":callID})
        print("---------------------------- NEW CUSTOMER ---------------------------")
        print("new customer added")
    print("customer already in konversation")
    return current_customer

@post('/voiceStart')
def test_response():
    body = request.body.read()
    print(body)
    callID = request.forms.get("callid")
    created = request.forms.get("created")
    callNumber = request.forms.get("from")
    print("callID:" + str(callID))
    print("created:" + str(created))
    print("callNUMBER:" + str(callNumber))
    newCustomer = checkCustomerVoice(callID, callNumber, created)
    startVoice = currentCollection.find_one({"pid":1})
    print(startVoice["voiceIVR"])
    messageVoice = startVoice["voiceIVR"]
    return json.dumps(messageVoice)

def checkVoice(keyPress, callID):
    current_customer = customers.find_one({"callID":callID})
    current_usecase = currentCollection.find_one({"pid":current_customer["request_ids"][-1]})
    print("---------------------------- CURRENT KUND ---------------------------")
    pprint(current_customer)
    print("---------------------------- CURRENT USE ---------------------------")
    pprint(current_usecase)
    if current_usecase == None:
        print("---------------------------- DICTIONARY ERROR ---------------------------")
        print("Please check the usecase dictionary for ", current_customer["request_ids"][-1])
        print("---------------------------- DICTIONARY ERROR ---------------------------")
        availableOptions = str(len(current_usecase["options"]))
        responseMessage = "Please respond with "
        responseCounter = 1
        for i in range(availableOptions):
            responseMessage += str(responseCounter)+", "
            responseCounter += 1
        response = responseMessage
        retain = True
        return response, retain
    else:
        print("Response approved: Returning response")
        responseFind = current_usecase["options"][int(keyPress)-1]
        print(responseFind)
        responseFind = responseFind["connection"]
        responseFind = currentCollection.find_one({"name": responseFind})
        response = responseFind["voiceIVR"]
        customers.update_one(current_customer,{"$push":{"request_responses":str(keyPress), "request_ids":responseFind["pid"]}})
    return response

@post('/voiceCont')
def test_response():
    body = request.body.read()
    print(body)
    keyPress = request.forms.get("result")
    callID = request.forms.get("callid")
    print(keyPress, type(keyPress))
    print(callID)
    messageVoice = checkVoice(keyPress, callID)
    return messageVoice

def recordURL(callID, fileURL):
    current_customer = customers.find_one({"callID":callID})
    print(current_customer)
    customers.update_one(current_customer,{"$set":{"recordingURL":fileURL}})
    return {"url-added": fileURL}

@post('/recordings')
def recordings():
    callID = request.forms.get("callid")
    fileURL = str(request.forms.get("wav"))
    print(callID, fileURL)
    return recordURL(callID, fileURL)

@get('/static/<path>')
def static(path):
    return static_file(path, "static")

def id_generator(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def startingPoint():
    start = currentCollection.find_one({"pid":1})
    response = start["smsIVR"]
    return response

@post('/smsDemo')
def demo_start():
    from_sender = request.forms.get("from")
    response = requests.post(
    'https://api.46elks.com/a1/conversations',
    auth = (config.elks_user, config.elks_pass),
    data = {
            "to": from_sender,
            "message":startingPoint(),
            "token":id_generator(),
            "reply_url": currentServer+"smsStart"
            }
    )
    print(response)

run(host='0.0.0.0', port=5501)