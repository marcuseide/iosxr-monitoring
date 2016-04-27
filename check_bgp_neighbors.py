#!/usr/bin/env python

# Nagios script that walks BGP-MIB and collects
# neighbors, state, asn and lastErrorTxt
# for both v4 and v6 peers.
#
# Use of the "-v" flag causes verbose output
# which can be useful for troubleshooting.
#
# Marcus Eide, SVT 2015


import sys
import netsnmp
import time
from optparse import OptionParser

#
# Options
#
def options():
    parser = OptionParser(usage="usage: %prog -H [host] -c [community] [-v]")
    
    parser.add_option("-H",
                      type="string",
                      dest="host",
                      help="hostname of bgp router"
                      )
  
    parser.add_option("-c",
                      type="string",
                      dest="community",
                      help="snmp community"
                      )
    
    parser.add_option("-v",
                      action="store_true",
                      dest="verbose",
                      help="use verbose output (no alarms raised)"
                      )
    
    (options, args) = parser.parse_args()
    
    if (not options.host or not options.community):
        parser.print_help()
        sys.exit(3) # Unknown
        
    return(options.host, options.community, options.verbose)

#
# Convert decimal character to hexadecimal character
#
def ipv6_converter(decimal):
    # .1.3.6.1.4.1.9.9.187.1.2.5.1.3.2.16.32.1.7.248.0.13.0.252.0.0.0.0.0.0.0.115
    # base                          .1.3.6.1.4.1.9.9.187.1.2.5.1.3.2.16
    # ip address in decimal form:   32.1.7.248.0.13.0.252.0.0.0.0.0.0.0.115
    #
    # 32 = 20
    # 1 = 01
    # 7 = 07
    # 248 = f8
    # 0 = 0
    # 13 = d
    # 0 = 0
    # = 2001:07f8:0d0
    # and so on...
  
    # Only convert double digit characters to hex
    # Fill single characters with leading zero
    if len(decimal) == 1:
        decimal = decimal.zfill(2)
    else:
        decimal = hex(int(decimal))[2:]
        
    return decimal

#
# Maps SNMP Integer state to more readable format
#
def get_state(stateint):
    if stateint == '1':
        state = 'IDLE'
    if stateint == '2':
        state = 'CONN'
    if stateint == '3':
        state = 'ACTV'
    if stateint == '4':
        state = 'OPENS'
    if stateint == '5':
        state = 'OPENC'
    if stateint == '6':
        state = 'ESTAB'
        
    return state

#
# Walk BGP-MIB and get v4 tables
#
def check_neighbor_status_v4(host,community):
    peers_v4   = {}
    asns_v4    = {}
    reasons_v4 = {}
  
    # Walk all peers from BGP-MIB
    oids_v4 = netsnmp.VarList( netsnmp.Varbind('.1.3.6.1.4.1.9.9.187.1.2.5.1.3.1.4'))
    res_v4  = netsnmp.snmpwalk( oids_v4, Version = 2, DestHost = host, Community = community)
  
    # Due to SNMP deamon lagg in the router, when switching communities from one to the other,
    # sometimes we fail to get snmp.
    # If we wait 5 sec and try again it should work just fine
    if not res_v4:
        time.sleep(5)
        oids_v4 = netsnmp.VarList( netsnmp.Varbind('.1.3.6.1.4.1.9.9.187.1.2.5.1.3.1.4'))
        res_v4  = netsnmp.snmpwalk( oids_v4, Version = 2, DestHost = host, Community = community)
        
    for oid_v4 in oids_v4:
        ipv4           = oid_v4.tag.replace("enterprises.9.9.187.1.2.5.1.3.1.4.", "")
        peers_v4[ipv4] = get_state(oid_v4.val)
    
        # Get RemoteAs from BGP-MIB
        asoid         = netsnmp.Varbind('.1.3.6.1.4.1.9.9.187.1.2.5.1.11.1.4.'+ipv4)
        asn           = netsnmp.snmpget( asoid, Version = 2, DestHost = host, Community = community )
        asns_v4[ipv4] = asn[0]
    
        # Get lastErrorTxt from BGP-MIB
        reasonoid        = netsnmp.Varbind('.1.3.6.1.4.1.9.9.187.1.2.5.1.28.1.4.'+ipv4)
        reason           = netsnmp.snmpget( reasonoid, Version = 2, DestHost = host, Community = community )
        reasons_v4[ipv4] = reason[0]
        
    return (peers_v4,asns_v4,reasons_v4)

#
# Walk BGP-MIB and get v6 tables
#
def check_neighbor_status_v6(host,community):
    peers_v6  = {}
    asns_v6   = {}
    reasons_v6= {}
  
    # Walk all peers from BGP-MIB
    oids_v6 = netsnmp.VarList( netsnmp.Varbind('.1.3.6.1.4.1.9.9.187.1.2.5.1.3.2.16'))
    res_v6  = netsnmp.snmpwalk( oids_v6, Version = 2, DestHost = host, Community = community )
  
    for oid_v6 in oids_v6:
        ipv6 = oid_v6.tag.split('.')
        oid  = oid_v6.tag
    
        # Convert into hexadecimal, each variable 16 bytes long
        a = ipv6_converter(ipv6[11]) +ipv6_converter(ipv6[12])
        b = ipv6_converter(ipv6[13]) +ipv6_converter(ipv6[14])
        c = ipv6_converter(ipv6[15]) +ipv6_converter(ipv6[16])
        d = ipv6_converter(ipv6[17]) +ipv6_converter(ipv6[18])
        e = ipv6_converter(ipv6[19]) +ipv6_converter(ipv6[20])
        f = ipv6_converter(ipv6[21]) +ipv6_converter(ipv6[22])
        g = ipv6_converter(ipv6[23]) +ipv6_converter(ipv6[24])
        h = ipv6_converter(ipv6[25]) +ipv6_converter(ipv6[26])
    
        # Remove leading zeroes
        a = a.lstrip("0")
        b = b.lstrip("0")
        c = c.lstrip("0")
        d = d.lstrip("0")
        e = e.lstrip("0")
        f = f.lstrip("0")
        g = g.lstrip("0")
        h = h.lstrip("0")
    
        # Contstruct properly formatted IPv6 address
        ipv6 = a +':' +b +':' +c +':' +d +':' +e +':' +f +':' +g
        ipv6 = ipv6.rstrip(":")
        ipv6 = ipv6 +'::' +h
    
        peers_v6[ipv6] = get_state(oid_v6.val)
    
        # Get RemoteAs from BGP-MIB
        oid           = oid.replace("enterprises.9.9.187.1.2.5.1.3.2.16.", "enterprises.9.9.187.1.2.5.1.11.2.16.")
        asoid         = netsnmp.Varbind(oid)
        asn           = netsnmp.snmpget( asoid, Version = 2, DestHost = host, Community = community )
        asns_v6[ipv6] = asn[0]
    
        # Get lastErrorTxt from BGP-MIB
        oid              = oid.replace("enterprises.9.9.187.1.2.5.1.11.2.16.", "enterprises.9.9.187.1.2.5.1.28.2.16.")
        reasonoid        = netsnmp.Varbind(oid)
        reason           = netsnmp.snmpget( reasonoid, Version = 2, DestHost = host, Community = community )
        reasons_v6[ipv6] = reason[0]
        
    return (peers_v6,asns_v6,reasons_v6)

#
# Main function
#
def main():
    exitcode    = 0
    total_peers = 0
    
    host,community,verbose = options()
    
    peers_up_v4   = []
    #peers_shut_v4 = []
    peers_up_v6   = []
    #peers_shut_v6 = []
    
    # Run checks
    peers_v4,asns_v4,reasons_v4 = check_neighbor_status_v4(host,community)
    peers_v6,asns_v6,reasons_v6 = check_neighbor_status_v6(host,community)
    
    # Exit if no neighbors at all, probably snmp failure
    if not peers_v4 and not peers_v6:
        print "No SNMP data"
        sys.exit(3) # Unknown
        
    if verbose:
        print "Neighbor\t\tAS\tState\tLast known reason"
        print "---------------------------------------------------------------"
  
    # Loop trough v4 peers
    for peer,state in peers_v4.iteritems():
        if verbose:
            print ("{0}\t\t{1}\t{2}\t{3}".format(
                peer,
                asns_v4[peer],
                state,
                reasons_v4[peer])
                   )
            total_peers += 1
        else:
            #if state != "ESTAB" and reasons_v4[peer] != 'administrative shutdown':
            if state != "ESTAB":
                print ("Neighbor {0} (AS{1}) is DOWN ({2}) -".format(
                    peer,
                    asns_v4[peer],
                    state)
                       ),
                exitcode = 2
            #elif state != "ESTAB" and reasons_v4[peer] == 'administrative shutdown':
            #    peers_shut_v4.append(peer)
            else:
                peers_up_v4.append(peer)
                
    # Loop through v6 peers      
    for peer,state in peers_v6.iteritems():
        if verbose:
            print ("{0}\t{1}\t{2}\t{3}".format(
                peer,
                asns_v6[peer],
                state,
                reasons_v6[peer])
                   )
            total_peers += 1
        else:
            #if state != "ESTAB" and reasons_v6[peer] != 'administrative shutdown':
            if state != "ESTAB":
                print ("Neighbor {0} (AS{1}) is DOWN ({2}) -".format(
                    peer,
                    asns_v6[peer],
                    state)
                       ),
                exitcode = 2
            #elif state != "ESTAB" and reasons_v6[peer] == 'administrative shutdown':
            #    peers_shut_v6.append(peer)
            else:
                peers_up_v6.append(peer)
    
    # Print summary
    if not verbose and exitcode == 0:
        #print ("{0} IPv4 neighbors ESTAB ({1} in ADMIN_DOWN), {2} IPv6 neighbors ESTAB ({3} in ADMIN_DOWN)".format(
        #    len(peers_up_v4),
        #    len(peers_shut_v4),
        #    len(peers_up_v6),
        #    len(peers_shut_v6))
        #       )
        print ("{0} IPv4 neighbors ESTAB, {1} IPv6 neighbors ESTAB").format(
            len(peers_up_v4),
            len(peers_up_v6),
               )
      
    if verbose:
        print "---------------------------------------------------------------"
        print 'Total number of peers:', total_peers
        
    # Exit
    sys.exit(exitcode)

#
#
#
if __name__ == "__main__":
    main()

