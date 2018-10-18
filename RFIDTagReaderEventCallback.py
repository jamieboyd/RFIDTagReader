#! /usr/bin/python
#-*-coding: utf-8 -*-
"""
Simple program to illustrate using a call back function with the Tag-In-Range
pin on the Innovations Design tag readers (ID-L3, ID-L12, ID-L20).
This is the general idea used in AutoMouseWeight Program

Last Modified:
2018/03/07 by Jamie Boyd - added some comments and a quit on ctrl-C
"""

from RFIDTagReader import RFIDTagReader
import RPi.GPIO as GPIO
from time import sleep

"""
#Serial Port and Tag-In-Range Pin (tirPin) must be modified to match your setup
"""
serialPort = '/dev/ttyUSB1'
#serialPort = '/dev/serial0'
tirPin=21

"""
tag and the TagReader object must be global so they can be used by the callback function
"""
tagReader = RFIDTagReader(serialPort, True, timeOutSecs = 0.05, kind='ID')
tag =0

"""
Threaded call back function on Tag-In-Range pin
Updates tag global variable whenever Tag-In-Range pin toggles
Setting tag to 0 means no tag is presently in range
"""
def tagReaderCallback (channel):
    global tag # the global indicates that it is the same variable declared above and also used by main loop
    if GPIO.input (channel) == GPIO.HIGH: # tag just entered
        try:
            tag = tagReader.readTag ()
        except Exception as e:
            tag = 0
    else:  # tag just left
        tag = 0

        

def main():

    global tag  # the global indicates that it is the same variable declared above and and also used by callback
    """"
    Setup tirPin for input, and install callback function, triggered on both rising and falling transistions
    """
    GPIO.setmode (GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup (tirPin, GPIO.IN)
    GPIO.add_event_detect (tirPin, GPIO.BOTH)
    GPIO.add_event_callback (tirPin, tagReaderCallback)
    print ("Waiting for tags....")
    while True:
        try:
            """
            Loop with a brief sleep, waiting for a tag to be read.
            After reading the tag, it is printed. This is the point
            where you might do something interesting
            """
            while tag==0:
                sleep (0.02)
            print ('Tag = ', tag)
            """
            Loop with a brief sleep, waiting for a tag to exit reading range
            """
            while tag != 0:
                sleep (0.02)
            print ('Tag went away')
        except KeyboardInterrupt:
            GPIO.cleanup()
            print ("Quitting")
            break
        

if __name__ == '__main__':
   main()
