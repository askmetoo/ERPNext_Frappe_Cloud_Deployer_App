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
    ###
    # This method will prepare the necessary data and call the methods 
    # which will deploy(upload) the json to the respective doctypes.
    ###
    try:
        skipAppList=['frappe', 'erpnext', 'deployer']
        print("Server is "+kwargs['server'])
        apps=frappe.get_installed_apps()
        exitCriteria=0
        for app in apps:
            if app in skipAppList:
                continue
            if os.path.exists(frappe.get_app_path(app,"fixtures")):
                fixture_file_list=sorted(os.listdir(frappe.get_app_path(app,"fixtures")))
                file_list_lenght=len(fixture_file_list)
                checkList=[]
                while fixture_file_list:
                    if file_list_lenght == len(fixture_file_list):
                        checkList=fixture_file_list.copy()
                        file_List_Lenght=len(fixture_file_list)
                    fname=file_list_lenght.pop()
                    if fname.endswith(".json"):
                        wholeJsonData=getJsonData(frappe.get_app_path(app,"fixtures",fname))
                        for jsonData in wholeJsonData:
                            if not uploadData(jsonData,fname,kwargs):
                                file_list_lenght.insert(0,fname)
                                file_List_Lenght=len(fixture_file_list)
                                break
                    if checkList == fixture_file_list:
                        raise Exception("Unable to deploy the following doctypes "+str(fixture_file_list)+". Reason: Some dependent doctypes could be missing.")
    except Exception as err:
        print(err)
        frappe.logger().error(frappe.utils.get_traceback())

def getJsonData(jsonFile):
    ###
    # Read the json file and convert it into json object
    ###
    with open(jsonFile) as f:
        jsonData=json.load(f)
    return jsonData

def uploadData(jsonData,fileName,kwargs):
    ###
    # Uploads the json data to the server
    ###
    userName=kwargs['user']
    password=kwargs['password']
    formatedAuthStr=userName+':'+password
    headers = {
        "Authorization":"basic "+str(base64.b64encode(formatedAuthStr.encode())),
        "Content-Type":"application/json",
        "Content-Type":"application/x-www-form-urlencoded"
    }
    api =kwargs['server']+"/api/resource/"+urllib.parse.quote(jsonData['doctype'])
    response = requests.post(api,headers=headers,data=json.dumps(removeUnwantedKeys(jsonData)),cookies=getCookie(kwargs))
    if response.status_code==417:
        return False
    if response.status_code==200:
        print("Successfully inserted "+jsonData['name']+" to "+jsonData['doctype'])
        frappe.logger().info("Successfully inserted "+jsonData['name']+" to "+jsonData['doctype'])
    elif response.status_code == 409 and response.reason == 'CONFLICT' :
        response = requests.put(api+"/"+urllib.parse.quote(jsonData['name']),headers=headers,data=json.dumps(removeUnwantedKeys(jsonData)),cookies=getCookie(kwargs))
        if response.status_code==417:
            print(response.status_code)
            return False
        elif response.status_code==200:
            if not 'data' in response.json():
                raise Exception("Unable to update the doctype "+jsonData['doctype']+ " Api is :"+api+"/"+urllib.parse.quote(jsonData['name']))
            print("Successfully updated "+jsonData['doctype']+" doctype with "+jsonData['name'] )
            frappe.logger().info("Successfully updated "+jsonData['doctype']+" doctype with "+jsonData['name'] )
        else:
            raise Exception("Exception while processing the request. Response code is "+str(response.status_code)+". Reason is "+response.reason)
    elif not response.status_code == 200:
        raise Exception("Exception while processing the request. Response code is "+str(response.status_code)+". Reason is "+response.reason)
    return True

def getCookie(kwargs):
    ###
    # Gets the session details from the cookie after login
    ###
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
    ###
    # Coverts the array to dictionary
    ###
    for val in tup:
        it = iter(val) 
        di.update(dict(zip(it, it)))
    return di

def removeUnwantedKeys(jsonData):
    ###
    # Removes unwanted keys, these keys are not required while sending the data to the server
    ###
    del_keys=('modified','modified_by', 'creation', 'owner', 'idx')
    for key in del_keys:
        if key in jsonData:
            del jsonData[key]
    return jsonData
 
            