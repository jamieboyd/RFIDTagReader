from RFIDTagReader import RFIDTagReader
import RPi.GPIO as GPIO
from time import sleep

serialPort = '/dev/serial0'
tirPin=21

tag =0
tagReader = RFIDTagReader(serialPort, True, timeOutSecs = 0.05, kind='ID')


"""
Threaded call back function on Tag-In-Range pin
Updates tag global variable whenever Tag-In-Range pin toggles
Setting tag to 0 means no tag is presently in range
"""
def tagReaderCallback (channel):
    global tag # the global indicates that it is the same variable declared above and also used by main loop
    if GPIO.input (channel) == GPIO.HIGH: # mouse just entered
        tag = tagReader.readTag ()
    else:  # mouse just left
        tag = 0

        

def main():

    global tag

    GPIO.setmode (GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup (tirPin, GPIO.IN)
    GPIO.add_event_detect (tirPin, GPIO.BOTH)
    GPIO.add_event_callback (tirPin, tagReaderCallback)
    while True:
        """
        Loop with a brief sleep, waiting for a tag to be read
        or a new day to start, in which case a new data file is made
        """
        while tag==0:
            sleep (0.02)
        print ('Tag = ', tag)
        while tag != 0:
            sleep (0.02)
        print ('Tag went away')
        

if __name__ == '__main__':
   main()
