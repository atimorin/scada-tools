#!/usr/bin/env python
# -*-mode: python; coding: UTF-8 -*-

import sys
import socket
import urllib
import re
import time
import calendar

#plc_ip = '10.0.70.155'
#plc_ver = 1200

plc_ip = '10.0.170.140'
plc_ver = 1500

time_gerex_1200 = re.compile(r'<div id="dynamic_date" class="updatable">.*[0-9]{4}', re.IGNORECASE)

time_gerex_1500_time = re.compile(r'([0-9]{2}:[0-9]{2}:[0-9]{2}) (am|pm)', re.IGNORECASE)
time_gerex_1500_date = re.compile(r'[0-9]{2}/[0-9]{2}/[0-9]{4}', re.IGNORECASE)

def get_uptime_timeticks():
    sysuptime_payload = '\x30\x27\x02\x01\x00\x04\x06\x70\x75\x62\x6c\x69\x63\xa0\x1a\x02\x02\x6f\x0c\x02\x01\x00\x02\x01\x00\x30\x0e\x30\x0c\x06\x08\x2b\x06\x01\x02\x01\x01\x03\x00\x05\x00'
    sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(sysuptime_payload, (plc_ip, 161))
    data, addr = sock.recvfrom(1024)
    data = data.encode('hex')
    t = data.split('2b06010201010300')[1] # split by object Name
    timeticks_len = int(t[2:4], 16)
    timeticks = int(data[-timeticks_len*2:], 16)
    return timeticks

def get_current_time_epoch():
    data = urllib.urlopen("http://{0}/Portal/Portal.mwsl?intro_enter_button=ENTER&PriNav=Start&coming_from_intro=true".format(plc_ip)).read()
    if plc_ver==1200:
        curr_time = time_gerex_1200.findall(data)[0].split('>')[1].replace('&nbsp;&nbsp;&nbsp;', ' ')
        curr_time_struct = time.strptime(curr_time, "%I:%M:%S %p %d.%m.%Y")
        curr_time_epoch = int(calendar.timegm(curr_time_struct))
    else:
        tmatch = time_gerex_1500_time.search(data)
        ctime = tmatch.group(0)
        dmatch = time_gerex_1500_date.search(data)
        cdate = dmatch.group(0)
        curr_time = '%s %s' % (ctime, cdate)
        curr_time_struct = time.strptime(curr_time, "%I:%M:%S %p %m/%d/%Y")
        curr_time_epoch = int(calendar.timegm(curr_time_struct))
    
    return curr_time_epoch

if __name__ == '__main__':
    
    timeticks = get_uptime_timeticks()
    curr_time_epoch = get_current_time_epoch()

    print "timeticks:", timeticks
    print "current time epoch:", curr_time_epoch

    plc_start_epoch = int( (curr_time_epoch - timeticks/100) & 0xFFFF )
    seed_range = (plc_start_epoch + 320, plc_start_epoch + 320 + 100)
    print "seed range:", seed_range
