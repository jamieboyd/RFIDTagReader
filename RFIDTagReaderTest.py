from RFIDTagReader import RFIDTagReader

    
serialPort = '/dev/serial0'
doCheckSum = True
nReads =5
try:
    tagReader = RFIDTagReader (serialPort, doCheckSum, timeOutSecs = None, kind='ID')
except Exception as e:
    raise e ("Error making RFIDTagReader")
i =0
while i < nReads:
    tag = tagReader.readTag ()
    print (tag)
    i += 1
print ('Read ' + str (nReads) + ' tags')
    
