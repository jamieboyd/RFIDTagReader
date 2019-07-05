#! /usr/bin/python
#-*-coding: utf-8 -*-

"""
 Imports: serial is needed for serial port communication with all RFID readers on all platforms.
 Install serial with pip if it is missing. RPi.GPIO is used only on the Raspberry Pi, and is only
 imported when a callback function is installed on the Tag in-Range Pin that is only on the ID tag readers
 Otherwise, RPi.GPIO is not imported
"""

import serial


"""
global variables and call back function for use on Raspberry Pi with
ID Tag Readers with Tag-In-Range pin
Updates RFIDtag global variable whenever Tag-In-Range pin toggles
Setting tag to 0 means no tag is presently in range of the reader
"""
GPIO = None
globalTag = 0
globalReader = None
def tagReaderCallback (channel):
    global globalTag # the global indicates that it is the same variable declared above
    if GPIO.input (channel) == GPIO.HIGH: # tag just entered
        try:
            globalTag = globalReader.readTag ()
        except Exception as e:
            globalTag = 0
    else:  # tag just left
        globalTag = 0
        globalReader.clearBuffer()



class TagReader:
    """
    Class to read values from an ID-Innovations RFID tag reader, such as ID-20LA
    or an RDM tag reader, like the 630. Only differece for the two tag reader types is
    that the ID readers return 2 more termination characters than the RDM reader.
    ID - RFID Tag is 16 characters: STX(02h) DATA (10 ASCII) CHECK SUM (2 ASCII) CR LF ETX(03h)
    RDM - RFID Tag is 14 characters: STX(02h) DATA (10 ASCII) CHECK SUM (2 ASCII) ETX(03h)
    Other important differences : 
    1) the ID readers have a Tag-In-Range pin that goes from low to high when a tag
    comes into range, and stays high till the tag leaves. This allows
    use of an interrput function on a GPIO event to read the tag. The RDM readers do
    not have a Tag-In-Range pin, although they do a tag-read pin, which gives a brief
    pulse when a tag is read, so an interrupt can still be used to read a tag, but not to
    tell when a tag has left the tag reader range. 
    2) The ID readers report the tag only once, when the tag first enters the reading range.
    The RDM readers report the tag value repeatedly as long as the tag is in range, with a
    frequency somewhere between 1 and 2 Hz.
    
    """
    def __init__(self, serialPort, doChecksum = False, timeOutSecs = None, kind='ID'):
        """
        Makes a new RFIDTagReader object
        :param serialPort:serial port tag reader is attached to, /dev/ttyUSB0 or /dev/ttyAMA0 for instance
        :param doCheckSum: set to calculate the checksum on each tag read
        :param timeOutSecs:sets time out value. Use None for no time out, won't return until a tag has ben read
        :param kind:the kind of tag reader used, either ID for ID-Innovations reader, or RDM 
        """
	# set data size based on kind paramater, for extra termination characters for ID tag readers
        if kind == 'RDM':
            self.kind = 'RDM'
            self.dataSize=14
        elif kind == 'ID':
            self.kind = 'ID'
            self.dataSize = 16
            self.TIRpin = 0
	# set field for time out seconds for reading serial port, None means no time out 
        self.timeOutSecs = timeOutSecs
	# set boolean for doing checksum on each read
        self.doCheckSum = bool(doChecksum)
	# initialize serial port
        self.serialPort = None
        try:
            self.serialPort = serial.Serial(str (serialPort), baudrate=9600, timeout=timeOutSecs)
        except Exception as anError:
            print ("Error initializing TagReader serial port.." + str (anError))
            raise anError
        if (self.serialPort.isOpen() == False):
            self.serialPort.open()
        self.serialPort.flushInput()
        

    def clearBuffer (self):
        """
        Clears the serial inout buffer for the serialport used by the tagReader
        """
        self.serialPort.flushInput()

    def readTag (self):
        """
        Reads a hexidecimal RFID tag from the serial port and returns the decimal equivalent

        :returns: decimal value of RFID tag, or 0 if no tag and non-blocking reading was specified
        :raises:IOError:if serialPort not read
        raises:ValueError:if either checksum or conversion from hex to decimal fails
        
        Clears buffer if there is an error. This will delete data in the serial buffer if
        more than one tag has been read before calling readTag. Use with code that is interested in
        what is near the tagReader right now, not what may have passed by in the past.
        """
        # try to read a single byte with requested timeout, which may be no timeout
        self.serialPort.timeout = self.timeOutSecs
        tag=self.serialPort.read(size=1)
        if (tag == b''): #if there is a timeout with no data, return 0
            return 0
        elif (tag == b'\x02'): # if we read code for start of tag, read rest of tag with short timeout
            self.serialPort.timeout = 0.025
            tag=self.serialPort.read(size=self.dataSize -1)
        else: # bad data. flush input buffer
            self.serialPort.flushInput()
            raise ValueError ('First character in tag was not \'\\x02\'')
        if tag.__len__() < self.dataSize -1  : # the read timed out with not enough data for a tag, so return 0
            self.serialPort.flushInput()
            raise ValueError ('Not enough data in the buffer for a complete tag')
        try:
            decVal = int(tag [0:10], 16)
        except ValueError:
            self.serialPort.flushInput()
            raise ValueError ("TagReader Error converting tag to integer: ", tag)
        else:
            if self.doCheckSum == True:
                if self.checkSum(tag [0:10], tag [10:12])== True:
                    return decVal
                else:
                    self.serialPort.flushInput()
                    raise ValueError ("TagReader checksum error: ", tag, ' : ' , tag [10:12])
            else:
                return decVal


    def checkSum(self, tag, checkSum):
        """
	Sequentially XOR-ing 2 byte chunks of the 10 byte tag value will give the 2-byte check sum

	:param tag: the 10 bytes of tag value
	:param checksum: the two bytes of checksum value
	:returns: True if check sum calculated correctly, else False
        """
        checkedVal = 0
        try:
            for i in range (0,5):
                checkedVal = checkedVal ^ int(tag [(2 * i) : (2 * (i + 1))], 16)
            if checkedVal == int(checkSum, 16):
                return True
            else:
                return False
        except Exception as e:
            raise e ("checksum error")
        

    def installCallback (self, tag_in_range_pin, callbackFunc = tagReaderCallback):
        """
        Installs a threaded call back for the tag reader, the default callback function
        being tagReaderCallback.
        :param tag_in_range_pin: the GPIO pin (in Broadcom numbering) connected to tag-in-range pin
        :param callbackFunc: a function that runs when tag-in-rrange-pin toggles, installed with PIO.add_event_detect
        
        tagReaderCallback uses the global references globalReader for
        the RFIDTagReader object, and globalTag for the variable updated with the RFID Tag number.
        the call back sets global variable globalTag when tag-in-range pin toggles, either
        to the new tag value, if a tag just entered, or to 0 if a tag left.
        You can install your own callback, as long as it uses RFIDTagReader.globalReader 
        and only references RFIDTagReader.globalTag  and other global variables and objects.
        """
        if self.kind == 'ID':
            global globalReader
            globalReader = self
            global GPIO
            GPIO = __import__ ('RPi.GPIO', globals(), locals(),['GPIO'],0) 
            GPIO.setmode (GPIO.BCM)
            GPIO.setmode (GPIO.BCM)
            GPIO.setup (tag_in_range_pin, GPIO.IN)
            self.TIRpin = tag_in_range_pin
            GPIO.add_event_detect (tag_in_range_pin, GPIO.BOTH)
            GPIO.add_event_callback (tag_in_range_pin, callbackFunc)


    def removeCallback (self):
        """
        Removes any calback function previously installed, and cleans up GPIO
        """
        if self.TIRpin != 0:
            GPIO.remove_event_detect (self.TIRpin)
            GPIO.cleanup(self.TIRpin)
            self.TIRpin == 0
            
    
    def __del__(self):
        """
        close the serial port when we are done with it
        """
        if self.serialPort is not None:
            self.serialPort.close()
        if self.kind == 'ID' and self.TIRpin != 0:
            GPIO.remove_event_detect (self.TIRpin)
            GPIO.cleanup (self.TIRpin)


    
