#!/usr/bin/env python

"""

mt_sync.py: This file queries the ManicTime database every 60 seconds and sends the activity results to CouchDB. It requires IronPython to communicate with SQL CE. It is possible to compile this to an EXE - please see the readme.

"""

import os
import ConfigParser
import clr
import sys
import json
import couchdb
from time import sleep
from datetime import datetime

config = ConfigParser.ConfigParser()
config.readfp(open('default.cfg'))

URL = config.get('CouchDB', 'url')
USERNAME = config.get('CouchDB', 'username')
PASSWORD = config.get('CouchDB', 'password')
DATABASE = config.get('CouchDB', 'database')
LOCATION = config.get('ManicTime', 'location')


clr.AddReference('System.Data.SqlServerCe, Version=4.0.0.0, Culture=neutral, PublicKeyToken=89845dcd8080cc91')
from System.Data.SqlServerCe import SqlCeConnection, SqlCeParameter

script_dirpath = os.path.dirname(os.path.join(os.getcwd(), __file__))
last_eventid_filepath = script_dirpath + "/last_eventid"

def get_last_eventid():
    last_eventid = 0
    # Open file containing the last event ID and get the last record read
    if os.path.isfile(last_eventid_filepath):
        try:
            last_eventid_file = open(last_eventid_filepath,'r')
            last_eventid = last_eventid_file.readline()
            last_eventid_file.close()
        # Catch the exception. Real exception handler would be more robust
        except IOError:
            sys.stderr.write('Error: failed to read last_eventid file, ' + last_eventid_filepath + '\n')
            sys.exit(2)
    else:
        sys.stderr.write('Error: ' + last_eventid_filepath + ' file not found! Starting from zero. \n')
    return last_eventid

def set_last_eventid(last_eventid):
    if last_eventid > 0:
        try:
            last_eventid_file = open(last_eventid_filepath,'w')
            last_eventid_file.write(str(last_eventid))
            last_eventid_file.close()
        # Catch the exception. Real exception handler would be more robust
        except IOError:
            sys.stderr.write('Error writing last_eventid to file: ' + last_eventid_filepath + '\n')
            sys.exit(2)
                
def query_database(last_eventid):
    conn_string = "Data Source=" + LOCATION + ";Persist Security Info=True"
    connection = SqlCeConnection(conn_string)
    connection.Open()
    command = connection.CreateCommand()

    command.CommandText = 'SELECT A.[GroupId], G.[DisplayName] as GroupDisplayName, A.[DisplayName], A.[StartUtcTime], A.[EndUtcTime], A.[ActivityId] FROM Activity A LEFT OUTER JOIN [Group] G ON A.[GroupId] = G.[GroupId] WHERE (A.[TimelineID] = @tID) AND (A.[ActivityID] > @aID) ORDER BY A.[ActivityId]'
    command.Parameters.Add(SqlCeParameter('tID', 3))
    command.Parameters.Add(SqlCeParameter('aID', last_eventid))

    ll = []

    reader = command.ExecuteReader()
    while reader.Read():
        print reader['ActivityId'], reader['StartUtcTime'], reader['EndUtcTime'], reader['DisplayName']
        temp_row = {}
        start = datetime(reader['StartUtcTime'])
        end = datetime(reader['EndUtcTime'])
        activityID = reader['ActivityId'] # Activity ID will also carry through to set_last_eventid below

        temp_row['action'] = "computer"
        temp_row['location'] = "home"
        temp_row['category'] = "activity"
        temp_row['start'] = start.strftime("%Y-%m-%dT%H:%M:%SZ")
        temp_row['end'] = end.strftime("%Y-%m-%dT%H:%M:%SZ")
        temp_row['added'] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        temp_row['message'] = reader['DisplayName']
        temp_row['ManicTimeActivityId'] = activityID
        temp_row['applicaiton'] = reader['GroupDisplayName']
        temp_row['quantity'] = (end-start).total_seconds()
        ll.append(temp_row)

    # set_last_eventid will exit the program if there is a problem with saving ActivityID
    set_last_eventid(activityID)

    couch = couchdb.Server(URL)
    couch.resource.credentials = (USERNAME, PASSWORD)
    db = couch[DATABASE]
    db.update(ll)

    connection.Close()
    
if __name__ == '__main__':
    while True:
        last_eventid = get_last_eventid()
        if last_eventid:
            query_database(last_eventid)
        sleep(60)
        