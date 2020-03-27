# ivrTreeCreator

### What you will need

* [A 46elks Account](www.46elks.com)
* Access to the 46elks Konversations API if you want to use the SMS functionality (can modify for regular SMS API)
* A free [mongoDB Atlas account](https://www.mongodb.com/cloud/atlas)
* If you want to use Google's Text-to-speech API then you need a [GCP Account](https://cloud.google.com/text-to-speech)

## Overview

There are currently three components to this repo:

1. The Builder API
2. The Builder Tool
3. The Demo Environment

The **'Builder API'** communicates with MongoDB and Google when creating branches/IVR etc. The builder API also receives input from the Builder tool. 

The **'Builder Tool'** is a simple command line interface to add branches, messages and options to your IVR or SMS tree. Currently this only supports building new trees and adding options to branches. In the future more functionality such as editing current messages and options will be available. 

The **'Demo Environment'** is a server that will run so that calls and text messages can interact with the IVR / SMS trees you have built

### The Builder API

You will need to update:

```
db = client.get_database("YOUR DATABASE")
first = db.YOUR COLLECTION #usecase collection
currentServer = "https://dca8234f.ngrok.io/"
```
### The Builder Tool

This is the tool that communicates with the API to build your IVR tree

```
1. New Path/Host, 2. New Options, 3. TODO list, 4. Current Paths/Hosts, 5. Current Tree, 6. Build IVR
```

1. New Paths are also hosts for new messages and new options. 

```
New Path Name = Welcome
New Path Message = Welcome to 46elks. Please choose from:
```
You will also be given the choice to ADD options immmeadietly 

2. New Options must be attached to a host (path) AND provide a connection to a new path (host)

```
New option Host = Welcome (This is the path the options are connected to)
New option Message = to speak with customer support (This is the available option)
New option Connection = Support (This is the connection that will trigger if this option is chosen)
```
3. TODO list is a list of hosts that need to be made to match with option connections

```
{"paths" : "Support"} - This means that the Support option needs to be created as a new path
```
4. Current Paths/Hosts refers to the available Paths/Hosts to add options to

```
{"list of paths" : ["Support", "Welcome"]} - This means that the Support option needs to be created as a new path
```
5. Returns a JSON of the current tree structure
```
{'state': [{'message': 'This is the start of your journey. What would you like to do?',
            'name': 'Start',
            'options': [{'connection': 'realm',
                         'message': 'Head into the realm',
                         'pid': 1}],
            'retain': True,
            'pid': 1,}
```
6. Builds the Voice IVR system using Google Text-to-speech (you will need to export your credentials correctly for this step to processes)[guide on credentials](https://cloud.google.com/docs/authentication/getting-started)

```
{'tree branches built': [{'name': 'deeper', 'pid': 3}]}
```
OR
```
{"tree branches built":"no tree to build, please add new paths and options"}
```
### The Demo Environment

You will need to update:

```
db = client.get_database("YOUR DATABASE")
first = db.YOUR COLLECTION #usecase collection
currentServer = "https://dca8234f.ngrok.io/"
```

AND the call forwarding options on your 46elks account.
