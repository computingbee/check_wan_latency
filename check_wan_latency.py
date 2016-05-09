#!/usr/bin/python

# Script:       check_wan_latency.py                                         
# Author:       Haris Buchal blog.computingbee.com                             
# Description:  Plugin for Nagios (and forks) to check WAN latency from a single 
#		location available on from www.super-ping.com online tool.
#     
#               THIS SOFTWARE COMES WITH ABSOLUTELY NO WARRANTY.
# License:      GPLv2
# Version:      1.0                                                               
# 20160505      Plugin initiated

import sys
import imp

#Nagios exit codes
STATE_OK=0
STATE_WARNING=1
STATE_CRITICAL=2
STATE_UNKNOWN=3

try:
	imp.find_module('argparse')
	import argparse as ap
	imp.find_module('IPy')
	import IPy as ipy
	imp.find_module('pycurl')
	import pycurl as pyc
	imp.find_module('StringIO')
	from StringIO import StringIO
except ImportError:
	print "One or more of required modules not installed, please refer to readme."
	sys.exit(STATE_UNKNOWN)

#valid cities on super-ping.com as of 20160505
DEF_CITY_ASIA = ("Hong-Kong","Christchurch","Singapore","Bangkok","Aukland")
DEF_CITY_AMER = ("Los-Angeles","Panama-City","New-York","Pittsburgh")
DEF_CITY_EURP = ("London","Barcelona","Istanbul","Milan","Kharkiv","Dusseldorf","Roubaix")

WAN_IP = ''
CITY = ""
TS_AVGLATW = 0
TS_AVGLATC = 0

def getuserinput():
	desc = """Checks latency to a public IP address from single geographical 
location as listed below. Locations are from www.super-ping.com website.
i.e New-York not New York

		Asia		Americas	Europe
		----		--------	------
		Hong-Kong	Los-Angeles	London
		Christchurch	Panama-City	Barcelona
		Singapore	New-York	Istanbul	
		Bangkok		Pittsburgh	Milan
		Aukland				Kharkiv
						Dusseldorf
						Roubaix
Exit status:
 0  if OK: the latency from specified city above is within given warning and critical
 1  if WARNING: more than warning threshold but less than critical
 2  if CRITICAL: more than critical threshold 
 3  if UNKNOWN: something went wrong

Report bugs to https://github.com/computingbee/check_wan_latency/issues"""
	parser = ap.ArgumentParser(description=desc,
			formatter_class=ap.RawTextHelpFormatter)
	parser.add_argument("ip",help="wan ip address to ping from remote location(s)")
	parser.add_argument("city",help="name of a city listed above. i.e. New-York")
	parser.add_argument("-w","--avglatw",type=float,help="warning latency threshold. i.e. 20 or 20.3")
	parser.add_argument("-c","--avglatc",type=float,help="critical latency threshold. i.e. 10 or 10.3")

	try:
       		args = parser.parse_args()
		
       	   	ipv4 = ipy.IP(args.ip)
		global WAN_IP
		WAN_IP = ipv4.strNormal()
		
		global TS_AVGLATW, TS_AVGLATC
		TS_AVGLATW = args.avglatw
		TS_AVGLATC = args.avglatc
	
		global CITY
		new_city = args.city
		if new_city in DEF_CITY_ASIA:
			CITY = new_city
		elif new_city in DEF_CITY_AMER:
			CITY = new_city
		elif new_city in DEF_CITY_EURP:
			CITY = new_city
		else:
			parser.exit(status=STATE_UNKNOWN, message="invalid city specified, exiting...\n")
	except ValueError:
		parser.exit(status=STATE_UNKNOWN, message="invalid ip {0} address\n".format(args.ip))

	except SystemExit:
		parser.exit(status=STATE_UNKNOWN,message="none")

# uses pycurl, will revise later to use lxml
def getlat4city():
	avglat = -1

	sp_url = "http://www.super-ping.com/ping.php?node=" + CITY + "&ping=" + WAN_IP
	sp_refer_url = "http://www.super-ping.com/?ping=" + WAN_IP + "&locale=en"
      	sp_http_headers = [ 'Referer: ' + sp_refer_url, 'X-Requested-With: XMLHttpRequest']

	crl = pyc.Curl()
	sio = StringIO()

	crl.setopt(pyc.URL, sp_url)
        crl.setopt(pyc.HTTPHEADER, sp_http_headers)
	crl.setopt(pyc.WRITEFUNCTION, sio.write)
	crl.perform()
	crl.close()
		
	lat_http_result = sio.getvalue() #process http result only if html
	if lat_http_result.strip() != "-" and lat_http_result.strip() != "super-ping.com":
		fstring="ping-avg'>"
		lstring="</div>"
		start = lat_http_result.index(fstring) + len(fstring)
		end = lat_http_result.index(lstring,start)
		avglat = lat_http_result[start:end]

	return float(avglat)

def checkstate(lat):
	if lat < 0:
		print "UNKNOWN: {0}ms, something must have gone wrong or your IP is unpingable".format(lat)
		sys.exit(STATE_UNKNOWN)
	elif TS_AVGLATW <= 0 or TS_AVGLATC <= 0:
		print "OK: {0}ms from {1}, no thresholds given or you just want see values first".format(lat,CITY)
		sys.exit(STATE_OK)
	elif TS_AVGLATW <= lat < TS_AVGLATC:
		print "WARNING: {0}ms from {1} is more than {2}ms but less than {3}ms for ip address {4}".format(lat,CITY,TS_AVGLATW,TS_AVGLATC,WAN_IP)
		sys.exit(STATE_WARNING)
	elif lat >= TS_AVGLATC:
		print "CRITICAL: {0}ms from {1} more than {2}ms for ip address {3}".format(lat,CITY,TS_AVGLATC,WAN_IP)
		sys.exit(STATE_CRITICAL)
	else:
		print "OK: {0}ms from {1}".format(lat,CITY)
		sys.exit(STATE_OK)
	

if __name__ == "__main__":
	
	getuserinput()
        
	lat = getlat4city()

	checkstate(lat)
