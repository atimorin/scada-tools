#!/usr/bin/env python

__author__ = "Aleksandr Timorin"
__copyright__ = "Copyright 2013, Positive Technologies"
__license__ = "GNU GPL v3"
__version__ = "1.7"
__maintainer__ = "Aleksandr Timorin"
__email__ = "atimorin@gmail.com"
__status__ = "Development"


import sys
from binascii import hexlify
from scapy.all import *
import optparse
import string

CODE = {
    'ENDC':0,  # RESET COLOR
    'RED':91,
}


def get_colorized_bytes(payload, cstart, cstop, color='RED'):
    cstart, cstop = int(cstart), int(cstop)
    if cstart*2 > len(payload) or cstop < cstart:
        return payload
    if cstop*2 > len(payload):
        cstop = len(payload)/2
    termcode_start = '\033[%sm' % CODE[color]
    termcode_stop  = '\033[%sm' % CODE['ENDC']
    d = dict(enumerate([payload[i:i+2] for i in range(0, len(payload), 2)], 1))
    d[cstart] = termcode_start + d[cstart]
    d[cstop]  = d[cstop] + termcode_stop
    colored_string = ''.join([d[i]  for i in sorted(d.iterkeys())])
    return colored_string



class PacketPayload(object):


    def __init__(self, num, src, dst, payload, colorize=None):
        self.packet_num = num
        self.src = src
        self.dst = dst
        self.payload = payload
        self.tpkt = ''
        self.cotp = ''
        self.s7   = ''
        self.colorize = colorize

    def parse_payload(self):
        if len(self.payload) >= 4*2:
            self.tpkt = self.payload[:4] == '0300' and self.payload[:8] or ''
            if len(self.payload) >= 7*2:
                #self.cotp = self.payload[8:12] == '02f0' and self.payload[8:14] or ''
                self.cotp = self.payload[8:14] or ''
                if len(self.payload) > 8*2:
                    data = self.payload[14:]
                    if data[:2] == '72':
                        self.s7 = data
                    else:
                        self.cotp += data

    def get_packet_as_text_by_src(self, src):
        if self.src == src:
            t_src = self.src
            t_dst = self.dst
            direction = '->'
        else:
            t_src = self.dst
            t_dst = self.src
            direction = '<-'
        if not self.colorize:
            __s7 = self.s7
        else:
            cstart, cstop = self.colorize.strip().split('-')
            __s7 = get_colorized_bytes(self.s7, cstart, cstop)       
        t = "{0:3} {1:15} {2:2} {3:15} : TPKT {4:8} | COTP {5:6} | S7 {6}".format(self.packet_num, t_src, direction, t_dst, self.tpkt, self.cotp, __s7)
        return t
    
    def get_printable(self):
        hexz = [ self.s7[i:i+2] for i in range(0, len(self.s7), 2)]
        p = ''.join([ chr(int(h, 16)) in string.letters+string.digits+string.punctuation+' ' and "{0:2}".format(chr(int(h, 16))) or '  '  for h in hexz ])
        t = "{0:3} {1:15} {2:2} {3:15} : {4:13} | {5:11} | S7 {6}".format('', '', '', '', '', '', p)
        return t


if __name__ == '__main__':
    
    parser = optparse.OptionParser()
    parser.add_option('-p', '--pcap', dest="pcap_file", help="traffic dump file")
    parser.add_option('-s', '--src', dest="src_show", help="source ip address", default="10.0.170.191")
    parser.add_option('--s7show', dest="s7show", action="store_true", help="show packets with nonzero s7", default=False)
    parser.add_option('-e', '--export', dest="export_s7", help="export all s7 payloads as hex stream to file")
    parser.add_option('-c', '--colorize', dest="colorize", help="colorize range of bytes. example: -c 2-4")
    parser.add_option('--sio', dest="srciponly", help="show packets only from <sio>")
    parser.add_option('--print', dest="printable", action="store_true", help="show printable characters of the payload", default=False)
    parser.add_option('--fpos', dest="fpos", help="show packets where field values=<fval> started from <fpos> and len=<flen>", default=0)
    parser.add_option('--flen', dest="flen", help="show packets where field values=<fval> started from <fpos> and len=<flen>", default=0)
    parser.add_option('--fval', dest="fval", help="show packets where field values=<fval> started from <fpos> and len=<flen>", default='0x00')
    options, args = parser.parse_args()
    pcap_file = options.pcap_file
    src_show = options.src_show
    export_s7 = options.export_s7
    s7show = options.s7show
    colorize = options.colorize
    srciponly = options.srciponly
    printable = options.printable
    fpos = int(options.fpos)
    fval = int(options.fval, 16)
    flen = int(options.flen)
    #if colorize:
    #    cstart, cstop = colorize.strip().split('-')
    #else:
    #    cstart = cstop = None
    #printhelp = options.printhelp
    #if printhelp:
    #    parser.print_help()
    
    packets = rdpcap(pcap_file)
    pnum = 0
    good_packets = []

    for packet in packets:
        pnum+=1
        src = None
        dst = None
        payload = None
        try:
            src = packet[IP].src
            dst = packet[IP].dst
            payload = packet[TCP].load.encode('hex')
        except (IndexError,AttributeError), e:
            print 'error in packet %d' % pnum
 
        if src and dst and payload:
            #tpkt = payload[:8]
            #iso8073 = payload[8:14]
            #s7 = len(payload)>16 and payload[14:] or ''
            #if tpkt.startswith('0300'):
            #    print "{0:3} {1:15} -> {2:15} : TPKT {3:8} | COTP {4:6} | S7 {5}".format(pnum, src, dst, tpkt, iso8073, s7)
            pp = PacketPayload(pnum, src, dst, payload, colorize)
            good_packets.append(pp)

    #src = good_packets[0].src
    #print src, good_packets[0].payload
    #sys.exit()
    if export_s7:
        export_s7_fh = open(export_s7, 'w', 0)
    for p in good_packets:
        p.parse_payload()
        if p.tpkt and p.cotp:
            if s7show and not p.s7:
                continue
            if srciponly and srciponly != p.src:
                continue
            if fpos and fval and flen:
                __v = p.s7[fpos*2-2:fpos*2+flen*2-2]
                if int(__v, 16) != fval:
                    continue
                
            print p.get_packet_as_text_by_src(src_show)
            if printable:
                print p.get_printable()
        if export_s7 and p.s7:
            #export_s7_fh.write(p.s7)
            export_s7_fh.write('%d\t%s\t%s\t%s\n' % (p.packet_num, p.src, p.dst, p.s7))
    if export_s7:
        export_s7_fh.close()


