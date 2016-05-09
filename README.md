#### Nagios & Icinga 2 plugin for checking latency to public IP address

Checks latency to a public IP address from single geographical 
location as listed below. Locations are from www.super-ping.com website.
i.e New-York not New York

                Asia            Americas        Europe
                ----            --------        ------
                Hong-Kong       Los-Angeles     London
                Christchurch    Panama-City     Barcelona 
                Singapore       New-York        Istanbul        
                Bangkok         Pittsburgh      Milan
                Aukland                         Kharkiv
                                                Dusseldorf
                                                Roubaix
Exit status:
 0  if OK: the latency from specified city above is within given warning and critical
 1  if WARNING: more than warning threshold but less than critical
 2  if CRITICAL: more than critical threshold 
 3  if UNKNOWN: something went wrong

#### Examples
```sh
./check_wan_latency.py 4.2.2.2 Milan
OK: 8.8ms from Milan, no thresholds given or you just want see values first

./check_wan_latency.py 4.2.2.2 New-York
OK: 0.9ms from New-York, no thresholds given or you just want see values first

./check_wan_latency.py 4.2.2.2 Hong-Kong
OK: 169.8ms from Hong-Kong, no thresholds given or you just want see values first

./check_wan_latency.py 4.2.2.2 Hong-Kong
OK: 170.2ms from Hong-Kong, no thresholds given or you just want see values first

./check_wan_latency.py 4.2.2.2 Hong-Kong -w 180 -c 200
OK: 173.4ms from Hong-Kong

./check_wan_latency.py 4.2.2.2 Hong-Kong -w 160 -c 200
WARNING: 169.8ms from Hong-Kong is more than 160.0ms but less than 200.0ms for ip address 4.2.2.2

./check_wan_latency.py 4.2.2.2 Hong-Kong -w 160 -c 165
CRITICAL: 170.6ms from Hong-Kong more than 165.0ms for ip address 4.2.2.2
```

#### Software  Requirements
```sh
It was tested on Python 2.7.6 and should work on 2.7.x. Following python modules are required: pycurl, 
StringIO, IPy
```

#### Usage
```sh
Before scheduling the check for an IP address, run the command without -w and -c to see min and max
returned for the latency from a location. In the Examples section above, we run the command from 
Hong-Kong a few times and then set wanring and critical thresholds for our checks.

Please see icinga2example.conf for setting this up on Icinga2. That's where I tested it but should work just
fine with Nagios and other forks.
```
