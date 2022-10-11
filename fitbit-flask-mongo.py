import string
from flask import Flask, request
import requests, json
from datetime import date, datetime, timedelta
from pymongo import MongoClient
import certifi
import time
client =MongoClient("mongodb+srv://ani4231:mongo123@fitbitcluster.3jqr7bo.mongodb.net/?retryWrites=true&w=majority",tlsCAFile = certifi.where())
db = client["fitbit_db"]
myheader = {"Authorization" : "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIyMzhSRFQiLCJzdWIiOiJCNEYzNVEiLCJpc3MiOiJGaXRiaXQiLCJ0eXAiOiJhY2Nlc3NfdG9rZW4iLCJzY29wZXMiOiJyc29jIHJzZXQgcm94eSBycHJvIHJudXQgcnNsZSByYWN0IHJsb2MgcnJlcyByd2VpIHJociBydGVtIiwiZXhwIjoxNjkzNDg4MDQxLCJpYXQiOjE2NjE5NTIwNDF9.uk4UyLwyQeLjnoE6jxKPNCxfkzs0mFTq_09cfuyV74U"}
app = Flask(__name__)
@app.route("/heartrate/last", methods=["GET"])
def get_heartrate():
    myurl5 = "https://api.fitbit.com/1/user/-/activities/heart/date/today/1d/15min.json"
    resp5 = requests.get(myurl5, headers=myheader).json()
    lastHR = resp5['activities-heart-intraday']['dataset'][len(resp5['activities-heart-intraday']['dataset'])-1]
    now = datetime.now()
    recorded_time =  datetime.strptime(str(lastHR['time']), "%H:%M:%S")
    recorded_time = recorded_time.replace(month=now.now().month, day=now.day, year=now.year)
    difference = now-recorded_time
    differenceInMinutes = difference.total_seconds()//60
    response = {'heart-rate': lastHR['value'],'time offset':int(differenceInMinutes)}
    return response

@app.route("/steps/last", methods=["GET"])
def get_Steps():
   myurl = "https://api.fitbit.com/1/user/-/activities/steps/date/today/1d/15min.json"
   resp = requests.get(myurl, headers=myheader).json()
   myurl2 = "https://api.fitbit.com/1/user/-/profile.json"
   resp2 = requests.get(myurl2, headers=myheader).json()
   steps = float(resp['activities-steps'][0]['value'])
   strideLength = resp2['user']['strideLengthWalking']
   distanceInCm = steps * strideLength
   distanceinMiles = distanceInCm/160934.4
   now = datetime.now()
   recorded_time = datetime.strptime(str(resp['activities-steps-intraday']['dataset'][len(resp['activities-steps-intraday']['dataset'])-1]['time']), "%H:%M:%S")
   recorded_time = recorded_time.replace(month=now.now().month, day=now.day, year=now.year)
   difference = now-recorded_time
   differenceInMinutes = difference.total_seconds()//60
   response = {'step-count':int(steps),'distance-miles':distanceinMiles,'time offset':int(differenceInMinutes)}
   return response

@app.route('/sleep/<string:userDate>', methods=["GET"])
def sleep(userDate: str):
    myurl = "https://api.fitbit.com/1.2/user/-/sleep/date/"+userDate+".json"
    resp = requests.get(myurl, headers=myheader).json()
    summaryStages = resp['summary']['stages']
    response = {'deep':summaryStages['deep'],'light':summaryStages['light'],'rem':summaryStages['rem'],'wake':summaryStages['wake']}
    return response

@app.route('/activity/<string:userDate>', methods=["GET"])
def activity(userDate: str):
    #dateObj = datetime.strptime(userDate, "%Y-%m-%d").date()
    myurl = "https://api.fitbit.com/1/user/-/activities/list.json?afterDate="+userDate+"&sort=asc&offset=0&limit=2"
    resp = requests.get(myurl, headers=myheader).json()
    response = {'very':0,'lightly':0,'fairly':0,'sedentary':0}
    for x in range(4):
        if resp['activities'][0]['activityLevel'][x]['minutes'] > 0:
            response[resp['activities'][0]['activityLevel'][x]['name']] +=resp['activities'][0]['activityLevel'][x]['minutes']

    return response

@app.route('/sensors/env', methods=["get"])
def getEnvSensors():
    latest_value = db.environmental_data.find().sort("timestamp",-1).limit(1)

    res = {"temp":0,"humidity":0,"timestamp": 0  }
    for x in latest_value:
        res["temp"] = x["temp"]
        res["humidity"] = x["humidity"]
        res["timestamp"] = x["timestamp"]

   
    return res

@app.route('/sensors/pose', methods=["get"])
def getPoseSensors():
    latest_value = db.pose_data.find().sort("timestamp",-1).limit(1)
    print(latest_value[0])

    res = {"presense":"","pose":"","timestamp":0}
    for x in latest_value:
        res["presense"] = x["presense"]
        res["pose"] = x["pose"]
        res["timestamp"] = x["timestamp"]   
    return res
  
@app.route('/post/env',methods=["post"])
def postEnv():
    res = request.get_json()
    jsonEdit = {"temp":res["temp"], "humidity":res["humidity"], "timestamp":time.time()}
    insert = db.environmental_data.insert_one(jsonEdit)
    return "ENV updated"

@app.route('/post/pose',methods=["post"])
def postPose():
    res = request.get_json()
    insert = db.pose_data.insert_one(res)
    return "Pose Database Updated"

if __name__ == '__main__':
    app.run(debug=True)