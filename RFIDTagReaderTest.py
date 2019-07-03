#! /usr/bin/python
#-*-coding: utf-8 -*-

"""
Simple test script for TagReader
Reads a few tags and prints them
Last Modified:
2018/03/07 by Jamie Boyd - added some comments, cleaned up a bit
"""

from RFIDTagReader import TagReader

"""
Change serialPort to wherever your tagreader is
and kind to 'ID' for ID-L3,12,20 etc. or RDM for RDM630 etc.
"""
#RFID_serialPort = '/dev/ttyUSB0'
RFID_serialPort = '/dev/serial0'
#RFID_serialPort='/dev/cu.usbserial-AL00ES9A'
RFID_kind = 'ID'
"""
Setting to timeout to None means we don't return till we have a tag.
If a timeout is set and no tag is found, 0 is returned.
"""
RFID_timeout = None
RFID_doCheckSum = True
nReads =3

try:
    tagReader = TagReader (RFID_serialPort, RFID_doCheckSum, timeOutSecs = RFID_timeout, kind=RFID_kind)
except Exception as e:
    raise e
print ('Waiting for tags...')
i = 0
while i < nReads:
    try:
        tag = tagReader.readTag ()
        i+=1
        print (tag)
    except ValueError as e:
        print (str (e))
        tagReader.clearBuffer()
print ('read all {:d} tags'.format (nReads))

