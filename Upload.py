
import time,signal,sys
import Adafruit_ADS1x15
import wiringpi
import csv
import datetime
import os

class GPIOHelper:
    def __init__(self): # Initializing the variables
        self.ILEDPin = 18
        self.samplingTime= 280
        self.deltaTime = 40
        self.sleepTime = 9680
        wiringpi.wiringPiSetupGpio()
        wiringpi.pinMode(self.ILEDPin,1)
        wiringpi.digitalWrite(self.ILEDPin,0)

    def readsensor(self): # function that read the sensor values
        adc = Adafruit_ADS1x15.ADS1115()
        GAIN = 2/3
        GAIN1 = 1
        f = open('dummyweather1.csv','a')

        while True:
            ts = time.time()
            #Generating time stamp
            stttime = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

            # reading mq135 values
            volts = (adc.read_adc(0,gain = GAIN)*0.1875)/1000   
            # Converting mq135 voltage reading to PPM
            ppm=volts*198
            voMeasured = 0
            vo = 0

            # Generating pulse to activate pm2.5 LED
            wiringpi.digitalWrite(self.ILEDPin,1)
            wiringpi.delayMicroseconds(self.samplingTime)
            wiringpi.delayMicroseconds(self.deltaTime)

            #reading the PM2.5 values
            vo = adc.read_adc(1,gain=GAIN1)



15

            voMeasured = ((vo)*0.125)
            wiringpi.digitalWrite(self.ILEDPin,0)
            wiringpi.delayMicroseconds(self.sleepTime)  
            dustDensity = (0.17 * voMeasured) - 0.1

            #writing to a file
            f.write(stttime+","+str(ppm)+","+str(dustDensity)+"\n")
            time.sleep(0.5)

helper = GPIOHelper()
helper.readsensor()

This program read the values from the sensors and then save it to a log file. 

#!/usr/bin/env python

from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from apiclient import errors
from apiclient.http import MediaFileUpload

try:
   import argparse
   flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
   flags = None


SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = 'client_secrets.json'
APPLICATION_NAME = 'elevate'
def update_file(service, file_id,
               new_filename, new_revision):

 try:
   file = service.files().get(fileId=file_id).execute()
   media_body = MediaFileUpload(
       new_filename, resumable=True)




16

   updated_file = service.files().update(
       fileId=file_id,
       body=file,
       newRevision=new_revision,
       media_body=media_body).execute()
   return updated_file
 except errors.HttpError as error:
   print ('An error occurred: %s' % error)
   return None

def get_credentials():
   home_dir = os.path.expanduser('~')
   credential_dir = os.path.join(home_dir, '.credentials')
   if not os.path.exists(credential_dir):
       os.makedirs(credential_dir)
   credential_path = os.path.join(credential_dir,
                                  'drive-elevate.json')

   store = Storage(credential_path)
   credentials = store.get()
   if not credentials or credentials.invalid:
       flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
       flow.user_agent = APPLICATION_NAME
       if flags:
           credentials = tools.run_flow(flow, store, flags)
       else: # Needed only for compatibility with Python 2.6
           credentials = tools.run(flow, store)
       print('Storing credentials to ' + credential_path)
   return credentials

def main():
   credentials = get_credentials()
   http = credentials.authorize(httplib2.Http())
   service = discovery.build('drive', 'v2', http=http)
   update_file(service,'1NzHMlWurOFurUBgZS5n1mVDFF6jlPY0_','dummyweather1.csv',True)

if __name__ == '__main__':
   main()

