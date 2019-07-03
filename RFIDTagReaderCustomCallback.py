#! /usr/bin/python3
#-*-coding: utf-8 -*-
"""
Simple program to illustrate using a custom call back function with the Tag-In-Range
pin on the Innovations Design tag readers (ID-L3, ID-L12, ID-L20). The custom callback
references a global object that counts entries and exits

Last Modified:
2019/03/22 by Jamie Boyd - initial version

"""
import RPi.GPIO as GPIO
import RFIDTagReader
from time import sleep

#serialPort = '/dev/ttyUSB0'
serialPort = '/dev/serial0'
tag_in_range_pin = 21 #16

# global object we will reference from custom callback function and main 
gObject = None

      
class myTestClass (object):
    """
    myTestClass makes a dictionary of entrances and exits for each tag number as it is encountered
    The dictionary of entrances and exits for each tag is itself saved in a dictionary whose keys are tags
    """
    
    def  __init__ (self):
        """
        class fields are tag, for current tag or 0 if no tag in range, and a dictionary to track entries/exits
        """
        self.tag = 0
        self.mDict = {}
        

    def run (self, tag):
        """
        On entry, tag number is saved to self.tag and dictionary of entries/exits is updated, creating an enrtry/exit
        dictionary for the tag if the tag does not already have one
        On exit, check that entry/exit dictionary exists for the tag, as exits must follow an entry, then update the
        dictionary entry for exist for this tag
        """
        if tag != 0: # this is an entry, with a tag number. Save tag number, and add entry to dictionary
            self.tag = tag
            if not self.tag in self.mDict.keys():
                self.mDict.update ({self.tag : {'entries' : 0, 'exits' : 0}})
            entries = self.mDict.get (self.tag).get ('entries') + 1
            self.mDict.get (tag).update ({'entries' : entries})
            print ('entry for {:d} = {:d}'.format(self.tag, entries))
        else: # this was an exit, with 0 passed as tag number
            if not self.tag in self.mDict.keys():
                print ('Exit before entry for tag {:d}'.format(self.tag))
            else:
                exits = self.mDict.get (self.tag).get ('exits') + 1
                self.mDict.get (self.tag).update ({'exits' : exits})
                print ('exits for {:d} = {:d}'.format(self.tag, exits))
            self.tag = 0
            
    @staticmethod
    def tagReaderCallback (channel):
        """
        call back that is installed with RFIDTagReader installcallback function. Notice that it calls
        tag reader function from the global object reference, RFIDTagReader.globalReader
        the callback also uses a global object of myTestclass, made in main and referenced as gObject
        """
        global gObject # the global indicates that it is the same variable declared above
        if GPIO.input (channel) == GPIO.HIGH: # tag just entered
            try:
                gObject.run (RFIDTagReader.globalReader.readTag ())
            except Exception as e:
                tag = 0
        else:  # tag just left
            RFIDTagReader.globalReader.clearBuffer()
            gObject.run (0)


    def printResults(self):
        """
        Prints results of entries and exits for all tags encountered
        """
        for key in self.mDict.keys():
            print ('for {:d}, entries  = {:d} and exits = {:d}'.format (key, self.mDict.get(key).get ('entries'), self.mDict.get(key).get ('exits')))

            
            

def main ():
    """
    make and obect of testClass, and make a global reference to that object that is called by callback
    """
    myObj = myTestClass()
    global gObject
    gObject = myObj
    """
    make a tag reader object, and install the custom callback. installCallBack
    makes a global reference to tagReader, RFIDTagReader.globalReader, to use in
    the custom callback
    """
    tagReader = RFIDTagReader.TagReader(serialPort, True, timeOutSecs = 0.05, kind='ID')
    tagReader.installCallback (tag_in_range_pin, callbackFunc = myTestClass.tagReaderCallback)
    """
    main loop does nothing but sleep, callback does all the work. On ctrl-C, get the
    testClass object to print its results, and cleanup and exit
    the results
    """
    print ("Waiting for tags....")
    try:
        while True:
            sleep (0.1)
    except KeyboardInterrupt:
        myObj.printResults()
        print ("Quitting")
        


if __name__ == '__main__':
   main()
