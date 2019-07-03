#! /usr/bin/python
#-*-coding: utf-8 -*-
"""Simple program to illustrate using a call back function with the Tag-In-Range
pin on the Innovations Design tag readers (ID-L3, ID-L12, ID-L20).
This is the general idea used in AutoMouseWeight Program

Last Modified:
2018/10/19 by Jamie Boyd - put callback and code to install callback in TagReader class
2018/03/07 by Jamie Boyd - added some comments and a quit on ctrl-C
"""
serialPort = '/dev/serial0'
#serialPort = '/dev/ttyUSB0'
tag_in_range_pin=21

import RFIDTagReader
from RFIDTagReader import TagReader
from time import sleep

def main ():

    tagReader = TagReader(serialPort, True, timeOutSecs = 0.05, kind='ID')
    tagReader.installCallback (tag_in_range_pin)
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
            del tagReader
            print ("Quitting")
            break
        

if __name__ == '__main__':
   main()
