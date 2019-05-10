#! /usr/bin/python
#-*-coding: utf-8 -*-
"""
Simple program to illustrate using a threaded custom call back function with the Tag-In-Range
pin on the Innovations Design tag readers (ID-L3, ID-L12, ID-L20).
This is the general idea used in AutoMouseWeight Program

Last Modified:
2018/10/19 by Jamie Boyd - put callback and code to install callback in TagReader class
2018/03/07 by Jamie Boyd - added some comments and a quit on ctrl-C
"""
serialPort = '/dev/serial0'
#serialPort = '/dev/ttyUSB0'
tag_in_range_pin=21


gracePeriod = 1


import RPi.GPIO as GPIO
import RFIDTagReader
from RFIDTagReader import TagReader
from time import time, sleep
from _thread import start_new_thread

globalReader = None
globalTag = 0
waitingForDelay = False

def graceThread (gracePeriod, tag):
    global globalTag
    global waitingForDelay
    endTime = time() + gracePeriod
    while time () < endTime and waitingForDelay:
        sleep (0.05)
    if waitingForDelay:
        globalTag = 0

def tagReaderGraceCallback (channel):
    global globalReader
    global globalTag # the global indicates that it is the same variable declared above
    global waitingForDelay
    if GPIO.input (channel) == GPIO.HIGH: # tag just entered
        waitingForDelay = False
        try:
            globalTag = globalReader.readTag ()
        except Exception as e:
            globalTag = 0
    else:  # tag just left - or did it? wait for the grace period before declaring this tag gone
        waitingForDelay = True
        thisTag = globalTag
        start_new_thread (graceThread, (gracePeriod, thisTag))
        globalReader.clearBuffer()



def main ():
    global globalReader
    global globalTag
    globalReader = TagReader(serialPort, True, timeOutSecs = 0.05, kind='ID')
    globalReader.installCallback (tag_in_range_pin, callbackFunc = tagReaderGraceCallback)
     
    print ("Waiting for tags....")
    while True:
        try:
            """
            Loop with a brief sleep, waiting for a tag to be read.
            After reading the tag, it is printed. This is the point
            where you might do something interesting
            """
            while globalTag == 0:
                sleep (0.02)
            print ('Tag = {:d}'.format(globalTag))
            while globalTag != 0:
                sleep (0.02)
            print ('Tag went away, really.')


        except KeyboardInterrupt:
            del globalReader
            print ("Quitting")
            break
        

if __name__ == '__main__':
   main()
