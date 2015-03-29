#!/usr/bin/env python
#
# dnsrotate.py:	script to determine fastest DNS server from among a list and rewrite resolver list
#		based on ranking of servers
#		Michael Liermann (michael.liermann.72@gmail.com), 2012

import subprocess, shlex, re, shutil, datetime
from operator import itemgetter

##Set the command options/variables.
testdomain='www.nasa.gov' 
querytype='A'
serverlist = open("/opt/scripts/dnsrotate/dnsservers", "r")
dnsservers = serverlist.readlines()
serverlist.close()
# below is dummy dictionary to hold test results
results = {'127.0.0.1': 9999}

# begin logging
logfile = open("/opt/scripts/dnsrotate/dnsrotate.log", 'a')
now = datetime.datetime.now()
nicedate = now.strftime("%Y-%m-%d %H:%M")
print('Beginning dnsrotate run at ' + nicedate + '\n') >> logfile
print('\n') >> logfile

# benchmark servers and store results in dictionary variable
for server in dnsservers:
    server = server.rstrip('\r\n')
    print('Testing server ' + server + '...\n') >> logfile
    cmd='/usr/bin/dig @' + server + " " +  testdomain + " " + querytype
    proc=subprocess.Popen(shlex.split(cmd),stdout=subprocess.PIPE)
    out=proc.communicate()[0]
    if "connection timed out" in out:
      serverspeed = 9999
      print('Server %s is not resonding.\n' % (server)) >> logfile
    else:
      querytime = re.search('(Query time:.*)',out)
      serverspeed = querytime.group(0)
      serverspeed = serverspeed.lstrip("Query time: ")
      serverspeed = serverspeed.rstrip(" msec")
      print('Server %s has response time of %s ms.\n' % (server, serverspeed)
    results[server] = int(serverspeed)
# now we need to sort the results and write to resolver list
serverlist = sorted(results.items(), key=itemgetter(1))
print('Tested servers ranked by response time: \n') >> logfile
shutil.copyfile('/etc/resolv.dnsmasq', '/etc/resolv.dnsmasq.bak')
resolvers = open('/etc/resolv.dnsmasq', 'w')
for host, time in serverlist:
  print(host + '\n') >> logfile
  if time != 9999:
    resolvers.write('nameserver ' + host + '\n')
resolvers.close()
print('New resolvers file for dnsmasq written - nonresponsive servers ignored.\n') >> logfile
print('Previous resolvers file backed up.\n') >> logfile
logfile.close()
  
  