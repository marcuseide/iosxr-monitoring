#!/usr/bin/env python
#
# Nagios script that checks enviromental
# sensors (temperature, voltage etc) on
# IOS XR devices
#
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

def snmp_get(host,community,oid):
    session = netsnmp.Session(Version   = 2,
                              DestHost  = host,
                              Community = community)
    
    session_oid = netsnmp.VarList(netsnmp.Varbind(oid))
    session_res = session.get(session_oid)
    
    return session_res

def get_entSensorType(host,community,index):
    entSensorType     = None
    entSensorType_res = snmp_get(host,community,'.1.3.6.1.4.1.9.9.91.1.1.1.1.1.'+index)
    
    if entSensorType_res[0] == '1':
        entSensorType = 'other'
    if entSensorType_res[0] == '2':
        entSensorType = 'unknown'
    if entSensorType_res[0] == '3':
        entSensorType = 'volts AC'
    if entSensorType_res[0] == '4':
        entSensorType = 'volts DC'
    if entSensorType_res[0] == '5':
        entSensorType = 'amperes'
    if entSensorType_res[0] == '6':
        entSensorType = 'watts'
    if entSensorType_res[0] == '7':
        entSensorType = 'hertz'
    if entSensorType_res[0] == '8':
        entSensorType = 'degrees celsius'
    if entSensorType_res[0] == '9':
        entSensorType = 'percent RH'
    if entSensorType_res[0] == '10':
        entSensorType = 'rpm'
    if entSensorType_res[0] == '11':
        entSensorType = 'cmm'
    if entSensorType_res[0] == '12':
        entSensorType = 'truthvalue'
    if entSensorType_res[0] == '13':
        entSensorType = 'special Enum'
    if entSensorType_res[0] == '14':
        entSensorType = 'dBm'
    
    return entSensorType

def get_entSensorScale(host,community,index):
    entSensorScale     = ""    
    entSensorScale_res = snmp_get(host,community,'.1.3.6.1.4.1.9.9.91.1.1.1.1.2.'+index)
    
    if entSensorScale_res[0] == '1':
        entSensorScale = 'yocto'
    if entSensorScale_res[0] == '2':
        entSensorScale = 'zepto'
    if entSensorScale_res[0] == '3':
        entSensorScale = 'atto'
    if entSensorScale_res[0] == '4':
        entSensorScale = 'femto'
    if entSensorScale_res[0] == '5':
        entSensorScale = 'pico'
    if entSensorScale_res[0] == '6':
        entSensorScale = 'nano'
    if entSensorScale_res[0] == '7':
        entSensorScale = 'micro'
    if entSensorScale_res[0] == '8':
        entSensorScale = 'milli'
    #if entSensorScale_res[0] == '9':
    #    entSensorScale = 'units'
    if entSensorScale_res[0] == '10':
        entSensorScale = 'kilo'
    if entSensorScale_res[0] == '11':
        entSensorScale = 'mega'
    if entSensorScale_res[0] == '12':
        entSensorScale = 'giga'
    if entSensorScale_res[0] == '13':
        entSensorScale = 'tera'
    if entSensorScale_res[0] == '14':
        entSensorScale = 'exa'
    if entSensorScale_res[0] == '15':
        entSensorScale = 'peta'
    if entSensorScale_res[0] == '16':
        entSensorScale = 'zetta'
    if entSensorScale_res[0] == '17':
        entSensorScale = 'yotta'
    
    return entSensorScale

def get_entSensorPrecision(host,community,index):  
    entSensorPrecision_res = snmp_get(host,community,'.1.3.6.1.4.1.9.9.91.1.1.1.1.3.'+index)
    entSensorPrecision     = entSensorPrecision_res[0]
    
    return entSensorPrecision

def get_entSensorValue(host,community,index):  
    entSensorValue_res = snmp_get(host,community,'.1.3.6.1.4.1.9.9.91.1.1.1.1.4.'+index)
    entSensorValue     = entSensorValue_res[0]
    
    return entSensorValue

def get_entSensorStatus(host,community,index):
    entSensorStatus     = None    
    entSensorStatus_res = snmp_get(host,community,'.1.3.6.1.4.1.9.9.91.1.1.1.1.5.'+index)
    
    if entSensorStatus_res[0] == '1':
        entSensorStatus = 'ok'
    if entSensorStatus_res[0] == '2':
        entSensorStatus = 'unavailable'
    if entSensorStatus_res[0] == '3':
        entSensorStatus = 'nonoperational'
        
    return entSensorStatus

def get_entSensorThresholdValue(host,community,index):
    #entSensorThresholdValue_min     = None
    #entSensorThresholdValue_max     = None
    entSensorThresholdValue_min_res = snmp_get(host,community,'.1.3.6.1.4.1.9.9.91.1.2.1.1.4.'+index+'.1')
    entSensorThresholdValue_max_res = snmp_get(host,community,'.1.3.6.1.4.1.9.9.91.1.2.1.1.4.'+index+'.2')
    entSensorThresholdValue_min     = entSensorThresholdValue_min_res[0]
    entSensorThresholdValue_max     = entSensorThresholdValue_max_res[0]
    
    
    return (entSensorThresholdValue_min, entSensorThresholdValue_max)

def get_entPhysicalDescr(host,community,index):   
    entPhysicalDescr_res = snmp_get(host,community,'.1.3.6.1.2.1.47.1.1.1.1.2.'+index)
    entPhysicalDescr     = entPhysicalDescr_res[0]
    
    return entPhysicalDescr

def main():
    host,community,verbose = options()
    exitcode               = 0
    total                  = 0
    
    session = netsnmp.Session(Version   = 2,
                              DestHost  = host,
                              Community = community)
    
    sensor_descriptions_oid = netsnmp.VarList(netsnmp.Varbind('.1.3.6.1.2.1.47.1.1.1.1.7'))
    sensor_descriptions_res = session.walk(sensor_descriptions_oid)

    for sensor_description in sensor_descriptions_oid:
        sensor_index       = sensor_description.tag.replace("mib-2.47.1.1.1.1.7.", "")
        sensor_description = sensor_description.val
        entSensorStatus    = get_entSensorStatus(host,community,sensor_index)

        #
        if entSensorStatus == 'ok':
            entSensorPrecision = get_entSensorPrecision(host,community,sensor_index)
            entPhysicalDescr   = get_entPhysicalDescr(host,community,sensor_index)
            entSensorValue     = get_entSensorValue(host,community,sensor_index)
            
            entSensorThresholdValue_min, entSensorThresholdValue_max = get_entSensorThresholdValue(host,community,sensor_index)

            entSensorThresholdValue_min          = int(entSensorThresholdValue_min)
            entSensorThresholdValue_max          = int(entSensorThresholdValue_max)
            entSensorPrecision                   = int(entSensorPrecision)
            entSensorThresholdPrecisionValue_min = entSensorThresholdValue_min
            entSensorThresholdPrecisionValue_max = entSensorThresholdValue_max
            
            entSensorPrecisionValue              = entSensorValue
            entSensorValue                       = int(entSensorValue)
            
            # Used max-value from 'show controller'
            if entPhysicalDescr == 'Transceiver Temperature Sensor':
                entSensorThresholdValue_min          = 0
                entSensorThresholdValue_max          = 700
                entSensorThresholdPrecisionValue_min = 0
                entSensorThresholdPrecisionValue_max = 70
                entSensorPrecisionValue              = entSensorPrecisionValue[:2] + '.' + entSensorPrecisionValue[2:]
            
            # Made up max-value    
            if entPhysicalDescr == 'Inlet Temperature SensorInlet0':
                entSensorThresholdValue_min          = 0
                entSensorThresholdValue_max          = 350
                entSensorThresholdPrecisionValue_min = 0
                entSensorThresholdPrecisionValue_max = 35
                entSensorPrecisionValue              = entSensorPrecisionValue[:2] + '.' + entSensorPrecisionValue[2:]
            
            # Made up max-value    
            if entPhysicalDescr == 'Hot Temperature SensorHotspot0':
                entSensorThresholdValue_min          = 0
                entSensorThresholdValue_max          = 550
                entSensorThresholdPrecisionValue_min = 0
                entSensorThresholdPrecisionValue_max = 55
                entSensorPrecisionValue              = entSensorPrecisionValue[:2] + '.' + entSensorPrecisionValue[2:]    

            if entSensorThresholdValue_min == -32768 or entSensorThresholdValue_max == -32768:
                continue

            if entSensorValue > entSensorThresholdValue_min and entSensorValue < entSensorThresholdValue_max:
                if verbose:
                    entSensorType = get_entSensorType(host,community,sensor_index)
                    print ("OK - Sensor \"{0} ({1})\" is reading {2} {3} (min:{4}, max:{5})".format(sensor_description,
                                                                                                         entPhysicalDescr,
                                                                                                         entSensorPrecisionValue,
                                                                                                         entSensorType,
                                                                                                         entSensorThresholdPrecisionValue_min,
                                                                                                         entSensorThresholdPrecisionValue_max)
                           )
                total += 1
            else:
                entSensorType = get_entSensorType(host,community,sensor_index)
                print ("WARNING - Sensor \"{0} ({1})\" is reading {2} {3} (min:{4}, max:{5})".format(sensor_description,
                                                                                                     entPhysicalDescr,
                                                                                                     entSensorPrecisionValue,
                                                                                                     entSensorType,
                                                                                                     entSensorThresholdPrecisionValue_min,
                                                                                                     entSensorThresholdPrecisionValue_max)
                       )
                exitcode = 2
                
        elif entSensorStatus == 'nonoperational':
            entPhysicalDescr = get_entPhysicalDescr(host,community,sensor_index)
            print ("WARNING - Sensor \"{0} ({1})\" is {2}".format(sensor_description,
                                                                  entPhysicalDescr,
                                                                  entSensorStatus)
                   )
            exitcode = 2

    if exitcode == 0 and not verbose:
        print ("All {0} sensors working and within threshold values".format(total))
        #print "All %s sensors working and within threshold values" % (total)
        
    sys.exit(exitcode)

if __name__ == "__main__":
  main()










