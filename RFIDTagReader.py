#! /usr/bin/python
#-*-coding: utf-8 -*-

import serial

class RFIDTagReader:
    """
    Class to read values from an ID-Innovations RFID tag reader, such as ID-20LA
    or an RDM tag reader, like the 630. Only differece for the two tag reader types is
    that the ID readers return 2 more termination characters than the RDM reader.
    ID - RFID Tag is 16 characters: STX(02h) DATA (10 ASCII) CHECK SUM (2 ASCII) CR LF ETX(03h)
    RDM - RFID Tag is 14 characters: STX(02h) DATA (10 ASCII) CHECK SUM (2 ASCII) ETX(03h)
    Other differences that do not affect this code but do change how you might use it are: 
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
            self.dataSize=14
        elif kind == 'ID':
            self.dataSize = 16
	# set field for time out seconds for reading serial port, None means no time out 
        self.timeOutSecs = timeOutSecs
	# set boolean for doing checksum on each read
        self.doCheckSum = bool(doChecksum)
	# initialize serial port
        self.serialPort = None
        try:
            self.serialPort = serial.Serial(str (serialPort), baudrate=9600, timeout=timeOutSecs)
        except IOError as anError:
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
            self.serialPort.timeout = 0.05
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
        for i in range (0,5):
             checkedVal = checkedVal ^ int(tag [(2 * i) : (2 * (i + 1))], 16)
        if checkedVal == int(checkSum, 16):
            return True
        else:
            return False


    
    def __del__(self):
        if self.serialPort is not None:
            self.serialPort.close()


if __name__ == '__main__':
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
    RFID_timeout = None
    RFID_doCheckSum = True
    nReads =5

    try:
        tagReader = RFIDTagReader (RFID_serialPort, RFID_doCheckSum, timeOutSecs = RFID_timeout, kind=RFID_kind)
        i =0
        while i < nReads:
            try:
                print ('Waiting for a tag....')
                tag = tagReader.readTag ()
                print ('Read a Tag', tag)
                i += 1
            except Exception as e:
                print (str(e))
                continue
        print ('Read ' + str (nReads) + ' tags')
        tagReader.__del__()
    except serial.serialutil.SerialException:
        print ('quitting...')

