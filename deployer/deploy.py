from pathlib import Path
import csv
import json, os
import frappe
import sys
import traceback
import base64
import requests
import urllib.parse

def startDeployment(**kwargs):
    try:
        print("Server is "+kwargs['server'])
        apps=frappe.get_installed_apps()
        for app in apps:
            if os.path.exists(frappe.get_app_path(app,"fixtures")):
                fixture_files=sorted(os.listdir(frappe.get_app_path(app,"fixtures")))
                for fname in fixture_files:
                    if fname.endswith(".json"):
                        wholeJsonData=getJsonData(frappe.get_app_path(app,"fixtures",fname))
                        for jsonData in wholeJsonData:
                            uploadData(jsonData,fname,kwargs)
    except Exception as err:
        print(err)
        frappe.logger().error(err)

def getJsonData(jsonFile):
    with open(jsonFile) as f:
        jsonData=json.load(f)
    return jsonData

def uploadData(jsonData,fileName,kwargs):
    userName=kwargs['user']
    password=kwargs['password']
    formatedAuthStr=userName+':'+password
    headers = {
        "Authorization":"basic "+str(base64.b64encode(formatedAuthStr.encode())),
        "Content-Type":"application/json",
        "Content-Type":"application/x-www-form-urlencoded"
    }
    api =kwargs['server']+"/api/resource/"+urllib.parse.quote(jsonData['doctype'])
    response = requests.post(api,headers=headers,data=json.dumps(jsonData),cookies=getCookie(kwargs))
    if response.status_code==200:
        print("Successfully inserted "+jsonData['name']+" to "+jsonData['doctype'])
        frappe.logger().info("Successfully inserted "+jsonData['name']+" to "+jsonData['doctype'])
    elif response.status_code == 409 and response.reason == 'CONFLICT' :
        response = requests.put(api+"/"+urllib.parse.quote(jsonData['name']),headers=headers,data=json.dumps(jsonData),cookies=getCookie(kwargs))
        if response.status_code==200:
            if not 'data' in response.json():
                raise Exception("Unable to update the doctype "+jsonData['doctype']+ " Api is :"+api+"/"+urllib.parse.quote(jsonData['name']))
            print("Successfully updated "+jsonData['doctype']+" doctype with "+jsonData['name'] )
            frappe.logger().info("Successfully updated "+jsonData['doctype']+" doctype with "+jsonData['name'] )
        else:
            raise Exception("Exception while processing the request. Response code is "+str(response.status_code)+". Reason is "+response.reason)
    elif (not response.status_code == 200) and (not response.status_code==417):
        raise Exception("Exception while processing the request. Response code is "+str(response.status_code)+". Reason is "+response.reason)

def getCookie(kwargs):
    response = requests.post(kwargs['server']+'/api/method/login', data = {'usr':kwargs['user'], 'pwd':kwargs['password']})
    if response.status_code == 200:
        delim="; "
        cookies=response.headers['Set-Cookie']
        cookieParts = []
        for index,val in enumerate(cookies.split(delim)):
            if 'Path=/,' in val:
                val= val.split(',')[1] if len(val.split(','))>0 else val.split(',')[0]
            cookieParts.append(val.split("="))
        di={}
        return createJson(cookieParts,di)
    else:
        raise Exception("Exception while connecting to the server. Response code is "+str(response.status_code)+". Reason is "+response.reason)

def createJson(tup, di): 
    for val in tup:
        it = iter(val) 
        di.update(dict(zip(it, it)))
    return di

