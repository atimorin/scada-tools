#!/usr/bin/env python

__author__ = "Aleksandr Timorin"
__copyright__ = "Copyright 2013, Positive Technologies"
__license__ = "GNU GPL v3"
__version__ = "1.7"
__maintainer__ = "Aleksandr Timorin"
__email__ = "atimorin@gmail.com"
__status__ = "Development"


# 2do:
# - show packets with required value in required place

import sys
from struct import unpack as unp
from copy import deepcopy
# ----------------------------------------

S7_PDU_TYPE = {
    0x01 : 'Connection init',
    0x02 : 'Data transfer',
}

S7_PACKET_TYPE = {
    0x31 : 'Request',
    0x32 : 'Response',
    0x33 : 'Keep-alive or cyclic',
}

S7_FUNCTION_CODE = {
    0x04ca : 'Connect. Init session',
    0x0542 : 'Write ?',
    0x0586 : '?',
    0x054c : 'Read ?',
    0x0524 : '?',
    0x006a : '?',
    0x04bb : '?',
    0x0017 : '?',        
}
# ----------------------------------------

class S7Packet:

    def __init__(self, payload):
        self.payload = payload # in hex as string
        self.hp = self.payload.decode('hex') # as normal hex values
        self.pp = {0: ('field_name', 'value', 'default comment', 0)}
        # fsize is size of field in bytes

    def is_s7(self):
        return 0x72 == unp('!B', self.hp[:1])[0]

    def add_field(self, name, value, comment='default comment', fsize=0):
        indx = max(self.pp.keys())+1
        self.pp[indx] = (name, value, comment, fsize)

    def shift_hp_data_left(self, hp):
        return hp[sum(map(lambda i: i[3], self.pp.values())) : ]

    def parse_payload(self):
        hp = deepcopy(self.hp)

        header, pdu_type, data_len, packet_type = unp('!BBHB', hp[:5])
        self.add_field('packet header', header, 's7 packet header', 1)
        self.add_field('pdu type', pdu_type, 'PDU type: '+ S7_PDU_TYPE[int(pdu_type)], 1)
        self.add_field('data len', data_len, 'data from next byte minus last 4 bytes', 2)
        self.add_field('packet type', packet_type, 'packet type: '+ S7_PACKET_TYPE[int(packet_type)], 1)
        hp = self.shift_hp_data_left(self.hp)
        
        #hp = hp[5:] # FIX IT EVERY TIME AFTER PARSNG NEW FIELD

        reserved1, function_code, reserved2 = unp('!HHH', hp[:6])
        self.add_field('reserved', reserved1, 'reserved?', 2)
        self.add_field('function code', function_code, 'function code: ' + S7_FUNCTION_CODE[int(function_code)], 2)
        hp = self.shift_hp_data_left(self.hp)
        self.add_field('reserved', reserved2, 'reserved?', 2)
        hp = self.shift_hp_data_left(self.hp)

        data_sequence_number, = unp('!H', hp[:2])
        self.add_field('data seq numb', data_sequence_number, 'data sequnce number ?', 2)
        hp = self.shift_hp_data_left(self.hp)


        
        # process unknow data and packet footer
        unparsed = unp('!%dB' % len(hp[:-4]), hp[:-4])
        self.add_field('unparsed', unparsed, 'unparsed/unknown data', len(unparsed))
        footer = unp('!I', hp[-4:])[0]
        self.add_field('packet footer', footer, 'packet footer with pdu type', 4)

    def print_packet(self):
        print "{0:25} : {1}".format('PACKET', repr(self.hp))
        print "{0:25} : {1}\n\n".format('PACKET AS STRING OF HEX\'s', self.payload)
        
        print "{0:20} : {1:5} : {2:128} : {3:6} : {4:40}".format('FNAME', 'FSIZE', 'VALUE', 'VSIZE', 'COMMENT')
        print "="*200
        del self.pp[0] # just remove init value
        
        for indx in sorted(self.pp.iterkeys()):
            field_name = self.pp[indx][0]
            #value = "0x0*x" % (self.pp[indx][3], self.pp[indx][1])
            field_size = "{0:#0{1}x}".format(self.pp[indx][3], 4)
            if field_name != 'unparsed':
                value = "{0:#0{1}x}".format(self.pp[indx][1], self.pp[indx][3]*2 + 2)
            else:
                value = '0x' + ''.join(map(lambda i: '{0:0{1}x}'.format(i, 2), self.pp[indx][1]))
            #value_size = "{0:#0{1}x}".format(len(self.pp[indx][3]), 6)
            value_size = "0x0000"
            comment = self.pp[indx][2]
            print "{0:20} : {1:5} : {2:128} : {3:6} : {4:40}".format( field_name, field_size, value, value_size, comment )
            print ".    "*40
        print ""
        



if __name__ == '__main__':
    for packet in open(sys.argv[1]):
        packet = packet.strip()
        if packet and not packet.startswith('#'):
            s7p = S7Packet(packet)
            #print s7p.is_s7()
            s7p.parse_payload()
            s7p.print_packet()
