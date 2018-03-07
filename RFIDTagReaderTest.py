#! /usr/bin/python
#-*-coding: utf-8 -*-

"""
Simple test script for TagReader
Reads a few tags and prints them
Last Modified:
2018/03/07 by Jamie Boyd - added some comments, cleaned up a bit
"""

from RFIDTagReader import RFIDTagReader

"""
Change serialPort to wherever your tagreader is
and kind to 'ID' for ID-L3,12,20 etc. or RDM for RDM630 etc.
"""
RFID_serialPort = '/dev/serial0'
RFID_kind = 'ID'
"""
Setting to timeout to none means we don't return till we have a tag.
If a timeout is set and no tag is found, 0 is returned.
"""
RFID_timeout = None
RFID_doCheckSum = True
nReads =5

try:
    tagReader = RFIDTagReader (RFID_serialPort, RFID_doCheckSum, timeOutSecs = RFID_timeout, kind=RFID_kind)
except Exception as e:
    raise e ("Error making RFIDTagReader")
i =0
print ('Waiting for a tag....')
while i < nReads:
    tag = tagReader.readTag ()
    print ('Read a Tag', tag)
    i += 1
print ('Read ' + str (nReads) + ' tags')

