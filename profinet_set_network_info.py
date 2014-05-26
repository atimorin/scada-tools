#!/usr/bin/env python

"""
File: profinet_set_network_info.py
Desc: Set network info: ip, mask, gateway through Profinet DCP request
"""

__author__ = "Aleksandr Timorin"
__copyright__ = "Copyright 2014, Positive Technologies"
__license__ = "GNU GPL v3"
__version__ = "0.1"
__maintainer__ = "Aleksandr Timorin"
__email__ = "atimorin@gmail.com"
__status__ = "Development"


import sys
import socket
import optparse

if __name__ == '__main__':
    

    parser = optparse.OptionParser()
    parser.add_option('-i', dest="src_iface", default="", help="source network interface")
    parser.add_option('--smac', dest="src_mac", default="", help="source mac address: 000102030405")
    parser.add_option('--dmac', dest="dst_mac", default="", help="destination mac address: aabbccddeeff")
    parser.add_option('--ip', dest="pf_ip", default="", help="ip address: 192.168.0.100")
    parser.add_option('--mask', dest="pf_mask", default="", help="network mask: 255.255.255.0")
    parser.add_option('--gw', dest="pf_gw", default="", help="default gateway: 192.168.0.1")
    options, args = parser.parse_args()
    parser.print_help()
    
    src_iface = options.src_iface or 'eth0'
    src_mac = options.src_mac
    dst_mac = options.dst_mac

    pf_ip = options.pf_ip
    pf_mask = options.pf_mask
    pf_gw = options.pf_gw

    raw_input("press any key to continue...")

    profinet_dcp_ethernet_frame = {
      'dst_mac' : dst_mac.decode('hex'),
      'src_mac' : src_mac.decode('hex'),
      'proto'   : '\x88\x92',
      'payload' : '\xfe\xfd\x04\x00\x04\x00\x00\x01\x00\x00\x00\x12\x01\x02\x00\x0e\x00\x00' + socket.inet_aton(pf_ip) + socket.inet_aton(pf_mask) + socket.inet_aton(pf_gw),
    }
    
    pdef = profinet_dcp_ethernet_frame
    eth_sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, 0x8892)
    # set socket recieve timeout 2 seconds
    # eth_sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, struct.pack('ii', int(2), 0))
    
    eth_sock.bind((src_iface, 0x8892))
    data = pdef['dst_mac'] + pdef['src_mac'] + pdef['proto'] + pdef['payload']
    eth_sock.send(data)

    recieved_packets = []

    while True:
        try:
            buf = eth_sock.recv(1024)
            print 'recieved: %r' % buf
            if buf:
                recieved_packets.append(buf)
            else:
                break
        except:
            break

    eth_sock.close()

