#!/usr/bin/env python

# Nagios script that walks CISCO-ENTITY-SENSOR-MIB
# and checks each individual sensors value.
#
# It also uses entSensorThresholdRelation to raise
# the correct alarm depending on the results according to:
#
#   "This variable indicates the relation between sensor value
#   (entSensorValue) and threshold value (entSensorThresholdValue), 
#   required to trigger the alarm. when evaluating the relation, 
#   entSensorValue is on the left of entSensorThresholdRelation, 
#   entSensorThresholdValue is on the right.
#
#   in pseudo-code, the evaluation-alarm mechanism is:
#
#   ...
#   if (entSensorStatus == ok) then
#   if (evaluate(entSensorValue, entSensorThresholdRelation, 
#   entSensorThresholdValue)) 
#   then
#   if (entSensorThresholdNotificationEnable == true)) 
#   then
#   raise_alarm(sensor's entPhysicalIndex);
#   endif
#   endif
#   endif
#   ..."
#
# Marcus Eide, SVT 2015

import netsnmp
import sys
from optparse import OptionParser

#
# Options
#
def options():
    parser = OptionParser(usage="usage: %prog -H [host] -c [community] [-v]")
    
    parser.add_option("-H",
                      type="string",
                      dest="host",
                      help="hostname of bgp router")
    
    parser.add_option("-c",
                      type="string",
                      dest="community",
                      help="snmp community")
    
    parser.add_option("-v",
                      action="store_true",
                      dest="verbose",
                      help="use verbose output")
    
    (options, args) = parser.parse_args()
    
    if (not options.host or not options.community):
        parser.print_help()
        sys.exit(3) # Unknown
        
    return(options.host, options.community, options.verbose)

# Walk entSensorStatus and save sensors with status "ok" in a list
def get_sensor_index(host,community):
    session = netsnmp.Session(Version   = 2,
                              DestHost  = host,
                              Community = community)
        
    oid = '.1.3.6.1.4.1.9.9.91.1.1.1.1.5'
    var = netsnmp.VarList(netsnmp.Varbind(oid))
    res = session.walk(var)
    
    indexes = []
    for v in var:
        
        #Object	entSensorStatus
        #OID	1.3.6.1.4.1.9.9.91.1.1.1.1.5
        #Type	SensorStatus 
        #1:ok
        #2:unavailable
        #3:nonoperational

        if v.val == "1":
            indexes.append(v.tag.replace("enterprises.9.9.91.1.1.1.1.5.",""))
    
    return (indexes)

# Function to use SNMP Get
def snmp_get(host,community,oid):
    session = netsnmp.Session(Version   = 2,
                              DestHost  = host,
                              Community = community)
    
    session_oid = netsnmp.VarList(netsnmp.Varbind(oid))
    session_res = session.get(session_oid)
    
    return (session_res)


def get_PhysicalClass(host,community,index):
    result = snmp_get(host,community,'.1.3.6.1.2.1.47.1.1.1.1.5.'+index)
    result = int(result[0])
    
    #Object	entPhysicalClass
    #OID	1.3.6.1.2.1.47.1.1.1.1.5
    #Type	PhysicalClass 
    #1:other
    #2:unknown
    #3:chassis
    #4:backplane
    #5:container
    #6:powerSupply
    #7:fan
    #8:sensor
    #9:module
    #10:port
    #11:stack
    #12:cpu
    
    if result == 1:
        result = 'other'
    if result == 2:
        result = 'unknown'
    if result == 3:
        result = 'chassis'
    if result == 4:
        result = 'backplane'
    if result == 5:
        result = 'container'
    if result == 6:
        result = 'powerSupply'
    if result == 7:
        result = 'fan'
    if result == 8:
        result = 'sensor'
    if result == 9:
        result = 'module'
    if result == 10:
        result = 'port'
    if result == 11:
        result = 'stack'
    if result == 12:
        result = 'cpu'
    
    return (result)

def get_PhysicalDescr(host,community,index):
    result = snmp_get(host,community,'.1.3.6.1.2.1.47.1.1.1.1.2.'+index)
    
    return (result[0])

def get_PhysicalName(host,community,index):
    result = snmp_get(host,community,'.1.3.6.1.2.1.47.1.1.1.1.7.'+index)
    
    return (result[0])

def get_SensorType(host,community,index):
    result = snmp_get(host,community,'.1.3.6.1.4.1.9.9.91.1.1.1.1.1.'+index)
    
    #Object	entSensorType
    #OID	1.3.6.1.4.1.9.9.91.1.1.1.1.1
    #Type	SensorDataType 
    #1:other
    #2:unknown
    #3:voltsAC
    #4:voltsDC
    #5:amperes
    #6:watts
    #7:hertz
    #8:celsius
    #9:percentRH
    #10:rpm
    #11:cmm
    #12:truthvalue
    #13:specialEnum
    #14:dBm
    
    if result[0] == '1':
        result = 'other'
    if result[0] == '2':
        result = 'unknown'
    if result[0] == '3':
        result = 'volts AC'
    if result[0] == '4':
        result = 'volts DC'
    if result[0] == '5':
        result = 'amperes'
    if result[0] == '6':
        result = 'watts'
    if result[0] == '7':
        result = 'hertz'
    if result[0] == '8':
        result = 'degrees celsius'
    if result[0] == '9':
        result = 'percent RH'
    if result[0] == '10':
        result = 'rpm'
    if result[0] == '11':
        result = 'cmm'
    if result[0] == '12':
        result = 'truthvalue'
    if result[0] == '13':
        result = 'special Enum'
    if result[0] == '14':
        result = 'dBm'
    
    return (result)

def get_SensorScale(host,community,index):
    result = snmp_get(host,community,'.1.3.6.1.4.1.9.9.91.1.1.1.1.2.'+index)
    
    #Object	entSensorScale
    #OID	1.3.6.1.4.1.9.9.91.1.1.1.1.2
    #Type	SensorDataScale 
    #1:yocto
    #2:zepto
    #3:atto
    #4:femto
    #5:pico
    #6:nano
    #7:micro
    #8:milli
    #9:units
    #10:kilo
    #11:mega
    #12:giga
    #13:tera
    #14:exa
    #15:peta
    #16:zetta
    #17:yotta
    
    if result[0] == '1':
        result = 'yocto'
    if result[0] == '2':
        result = 'zepto'
    if result[0] == '3':
        result = 'atto'
    if result[0] == '4':
        result = 'femto'
    if result[0] == '5':
        result = 'pico'
    if result[0] == '6':
        result = 'nano'
    if result[0] == '7':
        result = 'micro'
    if result[0] == '8':
        result = 'milli'
    if result[0] == '9':
        result = ' '
    if result[0] == '10':
        result = 'kilo'
    if result[0] == '11':
        result = 'mega'
    if result[0] == '12':
        result = 'giga'
    if result[0] == '13':
        result = 'tera'
    if result[0] == '14':
        result = 'exa'
    if result[0] == '15':
        result = 'peta'
    if result[0] == '16':
        result = 'zetta'
    if result[0] == '17':
        result = 'yotta'
    
    return (result)

def raise_alarm(host,community,index,value,threshold,txt):
    PhysicalClass = get_PhysicalClass(host,community,index)
    PhysicalDescr = get_PhysicalDescr(host,community,index)
    PhysicalName  = get_PhysicalName(host,community,index)
    SensorType    = get_SensorType(host,community,index)
    SensorScale   = get_SensorScale(host,community,index)
    
    print ("{2}: {0} ({1}) reads {3} {4} {5} which {7} {6} {4} {5}".format(
        PhysicalDescr,
        PhysicalName,
        PhysicalClass,
        value,
        SensorScale,
        SensorType,
        threshold,
        txt)
           )
    
    return(2)

def main():
    exitcode = 0
    num      = 0
    
    # Get options
    host,community,verbose = options()
    
    # Start with indexes that have a working sensor
    indexes = get_sensor_index(host,community)
    
    # Loop through them
    for index in indexes:
        
        # Each sensor has 6 possible values, so we need to loop through them aswell
        for i in xrange(1,7):
            i = str(i)
            
            # Skip sensors that don't report any value
            threshold    = snmp_get(host,community,'.1.3.6.1.4.1.9.9.91.1.2.1.1.4.'+index+'.'+i)
            threshold    = int(threshold[0])
            if threshold == -32768:
                continue
            
            # Count number of working sensors with sensible values
            num += 1
            
            # Get additional information for each sensor value
            value        = snmp_get(host,community,'.1.3.6.1.4.1.9.9.91.1.1.1.1.4.'+index)
            relation     = snmp_get(host,community,'.1.3.6.1.4.1.9.9.91.1.2.1.1.3.'+index+'.'+i)
            notification = snmp_get(host,community,'.1.3.6.1.4.1.9.9.91.1.2.1.1.6.'+index+'.'+i)
            
            # Make our results into integers
            value        = int(value[0])
            notification = int(notification[0])
            relation     = int(relation[0])

            #Object	entSensorThresholdRelation
            #OID	1.3.6.1.4.1.9.9.91.1.2.1.1.3
            #Type	SensorThresholdRelation 
            #1:lessThan
            #2:lessOrEqual
            #3:greaterThan
            #4:greaterOrEqual
            #5:equalTo
            #6:notEqualTo
            
            if relation == 1:
                if value < threshold:
                    if notification == 1:
                        txt = "is less than"
                        exitcode = raise_alarm(host,community,index,value,threshold,txt)
            
            if relation == 2:
                if value <= threshold:
                    # raise_alarm()
                    if notification == 1:
                        txt = "is less or equal than"
                        exitcode = raise_alarm(host,community,index,value,threshold,txt)
            
            if relation == 3:
                if value > threshold:
                    if notification == 1:
                        txt = "is greater than"
                        exitcode = raise_alarm(host,community,index,value,threshold,txt)
            
            if relation == 4:
                if value >= threshold:
                    if notification == 1:
                        txt = "is greater or equal than"
                        exitcode = raise_alarm(host,community,index,value,threshold,txt)

            if relation == 5:
                if value == threshold:
                    if notification == 1:
                        txt = "is equal to"
                        exitcode = raise_alarm(host,community,index,value,threshold,txt)
            
            if relation == 6:
                if value != threshold:
                    if notification == 1:
                        txt = "is not equal to"
                        exitcode = raise_alarm(host,community,index,value,threshold,txt)
    
    # Print summary if nothing raised an alarm
    if exitcode == 0:
        print ("All {0} sensors are working and all {1} values within limits".format(
            len(indexes),
            num)
               )
    
    # Exit
    sys.exit(exitcode)
    
# only execute when you want to run the module as a program
if __name__ == "__main__":
    main()


