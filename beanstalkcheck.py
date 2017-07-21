#!/usr/bin/python
import os
import sys, socket, io, json, getopt, time
import beanstalkc, logging

from datetime import datetime
from pprint import pprint

# checkActiveTubes = beanstalk.tubes()
# pprint(checkActiveTubes)
#
# useTubes = beanstalk.use('gtm_v35')
# pprint('active tubes => '+ useTubes)
#
# pprint(beanstalk.stats_tube('gtm_v35'))
#
# pprint(job.stats()['id'])

GTM_APPS_BS_VERSION = '1.0'
GTM_APPS_BS_HOST = ''
GTM_APPS_BS_PORT = ''
GTM_APPS_BS_TUBES = ''

SG_DO_BS_HOST = False
SG_DO_BS_PORT = False
SG_DO_TUBES = False

def info_main():
   print "Usage: %s [OPTIONS]" % os.path.basename(sys.argv[0])
   print "example: %s -a localhost -p 11300 -t gtm_v35 -b kickall" % os.path.basename(sys.argv[0])
   print ""
   print('Where OPTIONS:')
   print('-a HOST       Specify URL address of the beanstalk server')
   print('-p PORT       Specify Port of the beanstalk server')
   print('-t TUBES      Specify tubes of the beanstalk server')
   print('-b            To do job ex:kickall or kickjob')
   print('-h            Printing the help')
   print('-v            Print the version')
   print ""

def write_log(loglevel,logmsg):
    logging.basicConfig(filename='beanstalk-checker.log',level=logging.DEBUG)
    # logging.debug(arg)
    FORMAT = '%(asctime)s - %(name)s - [%(process)d] - %(levelname)s - %(message)s'
    logger = logging.getLogger(socket.gethostname())
    logger.setLevel(logging.DEBUG)
    if loglevel == "debug":
        logger.debug(logmsg)
    elif loglevel == "info":
        logger.info(logmsg)
    elif loglevel == "warn":
        logger.warn(logmsg, exc_info=True)
    elif loglevel == "error":
        logger.error(logmsg,exc_info=True)
    elif loglevel == "critical":
        logger.critical(logmsg, exc_info=True)

def do_kick_job_with_id_one_by_one(hosts, ports, tubes):
    beanstalk = beanstalkc.Connection(host=hosts, port=int(ports))
    useTubes = beanstalk.use(tubes)
    job = beanstalk.peek_buried()
    beanstalk.kick_job(job.stats()['id'])

def do_kick_job_all(hosts, ports, tubes):
    beanstalk = beanstalkc.Connection(host=hosts, port=int(ports))
    useTubes = beanstalk.use(tubes)
    job = beanstalk.peek_buried()
    beanstalk.kick(job.stats()['id'])

def do_delete_job_all(hosts, ports, tubes):
    beanstalk = beanstalkc.Connection(host=hosts, port=int(ports))
    useTubes = beanstalk.use(tubes)
    buriedCount = beanstalk.stats_tube(useTubes)['current-jobs-buried']
    for x in xrange(buriedCount):
        job = beanstalk.peek_buried()
        beanstalk.delete(job.stats()['id'])

def main(argv):
   if len(sys.argv) == 1:
       info_main()
   try:
      opts, args = getopt.getopt(argv,"a:p:t:b:hv")
   except getopt.GetoptError as err:
       write_log("error",err)
       info_main()
       sys.exit(2)
   for opt, arg in opts:
        if opt == "-v":
            print 'Version:', GTM_APPS_BS_VERSION
        elif opt == "-a":
            GTM_APPS_BS_HOST = arg
            SG_DO_BS_HOST = True
        elif opt == "-p":
            GTM_APPS_BS_PORT = arg
            SG_DO_BS_PORT = True
        elif opt == "-t":
            GTM_APPS_BS_TUBES = arg
            SG_DO_TUBES = True
        elif opt == "-b":
            GTM_APPS_BS_TODO = arg
            try:
                if SG_DO_BS_HOST|SG_DO_BS_PORT|SG_DO_TUBES == True:
                    if GTM_APPS_BS_TODO == "kickall":
                        do_kick_job_all(GTM_APPS_BS_HOST,GTM_APPS_BS_PORT,GTM_APPS_BS_TUBES)
                    elif GTM_APPS_BS_TODO == "delete":
                        do_delete_job_all(GTM_APPS_BS_HOST,GTM_APPS_BS_PORT,GTM_APPS_BS_TUBES)
                    else:
                        pass

            except Exception as e:
                write_log("error",e)
                sys.exit(e)
        elif opt in ("-h"):
            info_main()
            sys.exit()

if __name__ == "__main__":
   main(sys.argv[1:])
