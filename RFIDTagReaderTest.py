#! /usr/bin/python
#-*-coding: utf-8 -*-

"""
Simple test script for TagReader
Reads a few tags and prints them
Last Modified:
2018/03/07 by Jamie Boyd - added some comments, cleaned up a bit
"""

from RFIDTagReader import RFIDTagReader
import serial

"""
Change serialPort to wherever your tagreader is
and kind to 'ID' for ID-L3,12,20 etc. or RDM for RDM630 etc.
"""
RFID_serialPort = '/dev/ttyUSB0'
#RFID_serialPort = '/dev/serial0'
RFID_kind = 'ID'
"""
Setting to timeout to none means we don't return till we have a tag.
If a timeout is set and no tag is found, 0 is returned.
"""
RFID_timeout = 1
RFID_doCheckSum = True
nReads =100

def main ():
    try:
        tagReader = RFIDTagReader (RFID_serialPort, RFID_doCheckSum, timeOutSecs = RFID_timeout, kind=RFID_kind)
    except serial.serialutil.SerialException:
        print ('quitting....')
        return
    i =0
    try:
        while i < nReads:
            try:
                print ('Waiting for a tag....')
                tag = tagReader.readTag ()
                if tag != 0:
                    print ('Read a Tag', tag)
                    i += 1
            except (ValueError,serial.serialutil.SerialException) as e:
                print (str(e))
                continue
                
        print ('Read ' + str (nReads) + ' tags')
        tagReader.__del__()
    except KeyboardInterrupt:
        print ('quitting....')
    finally:
        tagReader.__del__()
    

if __name__ == '__main__':
    main()

