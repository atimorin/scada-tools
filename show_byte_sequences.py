#!/usr/bin/env python

import sys
import os
import itertools
import re
import random
import pprint
from copy import deepcopy

CODE = {
    'ENDC':0,  # RESET COLOR
    'BOLD':1,
    'UNDERLINE':4,
    'BLINK':5,
    'INVERT':7,
    'CONCEALD':8,
    'STRIKE':9,
    'GREY30':90,
    'GREY40':2,
    'GREY65':37,
    'GREY70':97,
    'GREY20_BG':40,
    'GREY33_BG':100,
    'GREY80_BG':47,
    'GREY93_BG':107,
    'DARK_RED':31,
    'RED':91,
    'RED_BG':41,
    'LIGHT_RED_BG':101,
    'DARK_YELLOW':33,
    'YELLOW':93,
    'YELLOW_BG':43,
    'LIGHT_YELLOW_BG':103,
    'DARK_BLUE':34,
    'BLUE':94,
    'BLUE_BG':44,
    'LIGHT_BLUE_BG':104,
    'DARK_MAGENTA':35,
    'PURPLE':95,
    'MAGENTA_BG':45,
    'LIGHT_PURPLE_BG':105,
    'DARK_CYAN':36,
    'AUQA':96,
    'CYAN_BG':46,
    'LIGHT_AUQA_BG':106,
    'DARK_GREEN':32,
    'GREEN':92,
    'GREEN_BG':42,
    'LIGHT_GREEN_BG':102,
    'BLACK':30,
}


RANDOM_COLORS = {
    'INVERT':7,
    'GREY30':90,
    'DARK_RED':31,
    'RED':91,
    'DARK_YELLOW':33,
    'YELLOW':93,
    'DARK_BLUE':34,
    'BLUE':94,
    'DARK_MAGENTA':35,
    'PURPLE':95,
    'DARK_CYAN':36,
    'AUQA':96,
    'DARK_GREEN':32,
    'GREEN':92,
}


def get_entry(substring, length=4):
    if length:
        yield substring[0:length]
    else:
        for stop in range(2,len(substring)+1):
            yield substring[0:stop]


def find_all_entries(pyaload_string, entry):
    return [m.start() for m in re.finditer(entry, payload_string)]


def get_colored_substrings_string(string, substring, color):
    termcode_start = '\033[%sm' % CODE[color]
    termcode_stop  = '\033[%sm' % CODE['ENDC']
    colored_string = string.replace(substring, termcode_start+substring+termcode_stop)
    return colored_string


if __name__ == '__main__':
    payloads_dict = dict(enumerate(x.strip().split('\t') for x in open(sys.argv[1])))
    length = len(sys.argv) > 2 and int(sys.argv[2]) or 2
    length = length*2
    #substrings_dict = {}
    found_entries = {} # key=ENTRY, value=(payloads indeces in payloads_dict)
    
    # main cycle for payload string
    for (payload_index, payload_data) in payloads_dict.items():
        entry_string = payload_data[3]

    
        for start in range(0, len(entry_string)-length+1, 2):
            entry = entry_string[start:length+start]
            #for entry in get_entry(entry_string[start:], length):
            if found_entries.has_key(entry):
                continue
            else:
                for (pi, pd) in payloads_dict.items():
                    payload_string = pd[3]
                    entries = find_all_entries(payload_string, entry)
                    if entries:
                        if found_entries.has_key(entry):
                            found_entries[entry].append((pi, len(entries)))
                        else:
                            found_entries[entry] = [ (pi, len(entries)) ]

                        

    
    #pprint.pprint(found_entries)

    #print "FOUND SEQUENCES: %d" % len(substrings_dict.keys())
    while True:
        os.system('clear')
        print "{0:4} : {1:{2}} : {3:6} : {4}\n".format('NUM', 'SEQ', length, 'ENTRIES', 'PACKETS')
        c = 0
        entries_by_c = {}
        for entry in found_entries.keys():
            total_entries = sum([ i[1] for i in found_entries[entry] ])
            packets = ','.join([ payloads_dict[i[0]][0] for i in found_entries[entry] ])
            if total_entries >= 2:
                c +=1
                entries_by_c[c] = entry
                print "{0:4} : {1:{2}} : {3:6} : {4}".format(c, entry, length, total_entries, packets )

        print "q - quit, s - show found entries, num - show entry"
        num = raw_input('num#')
        num = num.strip()
        if num=='q':
            sys.exit()
        elif num=='s':
            continue
        elif num.isdigit():
            num = int(num)
            entry = entries_by_c[num]
            print "="*80
            print "SELECTED ENTRY: %s" % entry
            print "{0:3} : {1:32} : {2}".format('PCK', 'DIR', 'PAYLOAD')
            color = random.choice(RANDOM_COLORS.keys())
            for data in found_entries[entry]:
                payload_index = data[0]
                packet_num, src, dst, payload_string = payloads_dict[payload_index]
                #value = substrings_dict[key]
                #print "{0:{1}} : {2}".format(key, length+2, ', '.join(map(str, value)))
                print "{0:3} : {1:32} : {2}".format(packet_num, '%s->%s' % (src,dst), get_colored_substrings_string(payload_string, entry, color ))
            raw_input('enter to continue#')


            #sys.exit()
            #for (key, value) in substrings_dict.items():
            #    print "{0:{1}} : {2}".format(key, length+2, ', '.join(map(str, value)))
            #    color = random.choice(RANDOM_COLORS.keys())
            #    print "{0:6} : {1}".format('ENTRIES', get_colored_substrings_string(string, key, color ))

