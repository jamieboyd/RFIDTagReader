#! /usr/bin/python3
#-*-coding: utf-8 -*-
"""
Simple program to illustrate using a custom call back function with the Tag-In-Range
pin on the Innovations Design tag readers (ID-L3, ID-L12, ID-L20). The custom callback
references a global object that counts entries and exits
"""
import RPi.GPIO as GPIO
import RFIDTagReader
from time import sleep

serialport = '/dev/ttyUSB0'
tag_in_range_pin = 16


gObject = None

class myTestClass (object):
    
    def  __init__ (self):
        #self.entries = entries
        #self.exits = exits
        self.tag = 0
        self.mDict = {}

    def run (self, tag, isEntry):
        if (isEntry):
            self.tag = tag
            if not self.tag in self.mDict.keys():
                self.mDict.update ({self.tag : {'entries' : 0, 'exits' : 0}})
            entries = self.mDict.get (self.tag).get ('entries') + 1
            self.mDict.get (tag).update ({'entries' : entries})
            print ('entry for {:d} = {:d}'.format(self.tag, entries))
        else:
            if not tag in self.mDict.keys():
                self.mDict.update ({tag : {'entries' : 0, 'exits' : 0}})
            exits = self.mDict.get (self.tag).get ('exits') + 1
            self.mDict.get (self.tag).update ({'exits' : exits})
            print ('exits for {:d} = {:d}'.format(self.tag, exits))
            self.tag = 0
            
            




def mytagReaderCallback (channel):
    global gObject # the global indicates that it is the same variable declared above
    if GPIO.input (channel) == GPIO.HIGH: # tag just entered
        try:
            #tag = RFIDTagReader.globalReader.readTag ()
            gObject.run (RFIDTagReader.globalReader.readTag (), True)
        except Exception as e:
            tag = 0
    else:  # tag just left
        #RFIDTagReader.globalTag = 0
        RFIDTagReader.globalReader.clearBuffer()
        gObject.run (0, False)




def main ():
    myObj = myTestClass()
    global gObject
    gObject = myObj

    
    tagReader = RFIDTagReader.TagReader(serialport, True, timeOutSecs = 0.05, kind='ID')
    
    tagReader.installCallBack (tag_in_range_pin, callBackFunc = mytagReaderCallback)
    print ("Waiting for tags....")
    while True:
        try:
            """
            Loop with a brief sleep, waiting for a tag to be read.
            After reading the tag, it is printed. This is the point
            where you might do something interesting
            """
            while RFIDTagReader.globalTag == 0:
                sleep (0.02)
            print ('Tag = ', RFIDTagReader.globalTag)
            """
            Loop with a brief sleep, waiting for a tag to exit reading range
            """
            while RFIDTagReader.globalTag != 0:
                sleep (0.02)
            print ('Tag went away')
        except KeyboardInterrupt:
            for key in myObj.mDict.keys():
                print ('for {:d}, entries  = {:d} exits = {:d}'.format (key, myObj.mDict.get(key).get ('entries'), myObj.mDict.get(key).get ('exits')))
            #print ('Entries total = {:d}, exits total = {:d}\n'.format (myObj.entries, myObj.exits))
            GPIO.cleanup()
            print ("Quitting")
            break
        

if __name__ == '__main__':
   main()
