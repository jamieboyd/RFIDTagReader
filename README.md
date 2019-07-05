# RFIDTagReader
Python class to read values from an ID-Innovations RFID tag reader, such as ID-20LA  or an RDM tag reader, like the 630. It reads EM4100 format tags. Also contains code showing how to use the Tag-In-Range pin as a GPIO interrupt on Raspberry Pi.

Imports:
serial is needed for serial port communication with all RFID readers on all platforms. Install serial with pip if it is missing.
RPi.GPIO is used only on the Raspberry Pi, and is only imported when a callback function is installed on the Tag in-Range Pin that is only on the ID tag readers Otherwise, RPi.GPIO is not imported
 
RFIDTagReader.py 
contains the class the defines the TagReader.
__init__(self, serialPort, doChecksum = False, timeOutSecs = None, kind='ID'):
        Makes a new RFIDTagReader object
	
        :param serialPort:serial port tag reader is attached to, /dev/ttyUSB0 or /dev/ttyAMA0 for instance
        :param doCheckSum: set to calculate the checksum on each tag read
        :param timeOutSecs:sets time out value. Use None for no time out, won't return until a tag has ben read
        :param kind:the kind of tag reader used, either ID for ID-Innovations reader, or RDM 

clearBuffer (self):
        Clears the serial inout buffer for the serial port used by the tagReader
        

readTag (self):
        Reads a hexidecimal RFID tag from the serial port and returns the decimal equivalent

        :returns: decimal value of RFID tag, or 0 if no tag and non-blocking reading was specified
        :raises:IOError:if serialPort not read
        raises:ValueError:if either checksum or conversion from hex to decimal fails
        
Clears buffer if there is an error. This will delete data in the serial buffer if more than one tag has been read before calling readTag. Use with code that is interested in what is near the tagReader right now, not what may have passed by in the past.


checkSum(self, tag, checkSum):
	Sequentially XOR-ing 2 byte chunks of the 10 byte tag value will give the 2-byte check sum

	:param tag: the 10 bytes of tag value
	:param checksum: the two bytes of checksum value
	:returns: True if check sum calculated correctly, else False
	
TagReaderCallback (channel):
	The default callback function, uses a global reference to a TagReader to set a global variable to the value of the read tag. 

installCallback (self, tag_in_range_pin, callbackFunc = tagReaderCallback):
        Installs a threaded call back for the tag reader, the default callback function being tagReaderCallback.
	
        :param tag_in_range_pin: the GPIO pin (in Broadcom numbering) connected to tag-in-range pin
        :param callbackFunc: a function that runs when tag-in-rrange-pin toggles, installed with PIO.add_event_detect
        
tagReaderCallback uses the global references globalReader for the RFIDTagReader object, and globalTag for the variable updated with the RFID Tag number.  The call back sets global variable globalTag when tag-in-range pin toggles, either to the new tag value, if a tag just entered, or to 0 if a tag left. You can install your own callback, as long as it uses RFIDTagReader.globalReader and only references RFIDTagReader.globalTag  and other global variables and objects.


RFIDTagReader_setup.py
Set-up code that copies RFIDTagReader.py into the standard Python lbraries folder. Run with the command
sudo python3 RFIDTagReader_setup.py install


RFIDTagReaderTest.py
Simple test script for TagReader, without using the tag-In-range pin. Reads a few tags and prints them.

Some global variables at top of the file are used to adjust settings:
Set RFID_serialPort to wherever your tagreader is. Some common values for Linux and MacOs are provided, so they can simply be uncommented as needed:
#RFID_serialPort = '/dev/ttyUSB0'
RFID_serialPort = '/dev/serial0'
#RFID_serialPort='/dev/cu.usbserial-AL00ES9A'

Set RFID_kind to 'ID' for ID-L3,12,20 etc. or RDM for RDM630 etc.

Set RFID_timeout to timeout value in seconds. If no tag is read before the timeout expires, 0 is returned. Set RFID_timeout to None to not return till we have a tag.

Set RFID_kind to 'ID' for ID-L3,12,20 etc. or RDM for RDM630 etc.

Set nReads to the number of times you want the tagReader to read a tag before the program exits.

Three progressively more complicated examples of using a callback function with the tag-in-range pin are also provided.

1 - RFIDTagReaderEventCallBack.py
Demonstrates using the default callback function provided in RFIDTagReader.py

Set global variable tag_in_range_pin to the GPIO pin attached to the TIR pin on the tag reader.

The program first runs tagReader.installCallback (tag_in_range_pin). The program then loops continuously until control-c is pressed, printing the number of a tag, from RFIDTagReader.globalTag,  whenever a tag is read and printing 'Tag went away' when a tag is no longer in reading range.

2 - RFIDTagReaderCustomCallback.py
Demonstrates installing a custom callback with TagReader. The custom callback references a global object that counts entries and exits for each tag.  The class of the object, myTestClass, is defined in the file. 
The program makes an object of myTestClass, and makes global reference to it, makes a tag reader object, and installs the custom callback. In the callback, myTestClass.tagReaderCallback, calls the tag reader function from the global object reference, RFIDTagReader.globalReader. The callback also uses a global reference to the object of myTestclass, made in main and referenced as gObject.  the gObject saves the tag number  to self.tag and a dictionary of entries/exits is updated, creating an enrtry/exit dictionary for the tag if the tag does not already have one. The main loop does nothing but sleep and check for exceptions, as the callback does all the work. On ctrl-C,  the testClass object prints its results and the program exits.

3 - RFIDTagReaderGraceCallback.py
In this example, a separate thread is started by the callback function. The purpose is to give a grace period in which a tag may momentarily leave  reading range, but will not be counted as having exited if the same tag is read again before a certain grace time has expired. 
