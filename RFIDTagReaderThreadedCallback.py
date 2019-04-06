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
#serialPort = '/dev/serial0'
serialPort = '/dev/ttyUSB0'
tag_in_range_pin=16#21

import RPi.GPIO as GPIO
import RFIDTagReader
from RFIDTagReader import TagReader
from time import time, sleep
from _thread import start_new_thread


gracePeriod = 0.5
def graceThread (leftTime, tag):
    sleep (gracePeriod)
    global globalTag
    global waitingForDelay
    if tag == globalTag and waitingForDelay:
        globalTag = 0
        waitingForDelay = False

globalTag = 0
globalReader = None
def tagReaderCallback (channel):
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
        start_new_thread (time () + gracePeriod, globalTag)
        globalReader.clearBuffer()
