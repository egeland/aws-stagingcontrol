#!/usr/bin/env python

import boto.ec2
import stagingcontrol
import os, sys
import argparse
from boto.exception import EC2ResponseError, NoAuthHandlerFound

parser = argparse.ArgumentParser(description='Stop or start non-prod EC2 instances')
parser.add_argument("-p", "--pony", action="store_true", help="This script has magical powers")
parser.add_argument("-f", "--force", action="store_true", help="Force the action (start|stop) to happen without prompting")
parser.add_argument("-n", "--dryrun", action="store_true", help="Simulate everything - print out what would have been done", default=False)
arg_group1 = parser.add_mutually_exclusive_group(required=False)
arg_group1.add_argument("-v", "--verbose", action="store_true", help="Show more output")
arg_group1.add_argument("-q", "--quiet", action="store_true", help="Show no output")
arg_group = parser.add_mutually_exclusive_group(required=True)
arg_group.add_argument("-c", "--check", action="store_true", help="Show the current status of the instances")
arg_group.add_argument("-r", "--start", action="store_true", help="Start the instances up")
arg_group.add_argument("-s", "--stop", action="store_true", help="Stop the instances")
parser.add_argument("-i", "--id", help="AWS Credentials file", default='~/amazon/certs/'+os.getenv('USER')+'.credentials')
parser.add_argument("instancelist", help="The list of instances to work with")
args = parser.parse_args()

if args.pony:
    stagingcontrol.pony()

if args.dryrun:
    args.verbose = True
    args.quiet = False

if args.verbose:
    print "Using {0} to connect".format(args.id)
stagingcontrol.set_aws_credentials(args.id)

try:
    conn = boto.ec2.connect_to_region('ap-southeast-2')
    undef = conn.describe_account_attributes()
except (EC2ResponseError, NoAuthHandlerFound) as e:
    if args.verbose:
        print "The credentials are incorrect: {0}".format(e.error_message)
    sys.exit(1)

tlist = stagingcontrol.ServerList(args.instancelist,conn)
actionlist = tlist.parse()
tlist.save(dryrun=args.dryrun)

if len(actionlist) <= 0: # Nothing to action
    if args.verbose:
        print "The server list in {0} contains no actionable instances".format(args.instancelist)
    conn.close()
    sys.exit(1)

if args.verbose and (args.stop or args.start):
    print "You are about to act on these instances"
    for item in actionlist:
        print item.id
    print ""

if (args.stop or args.start) and not (args.dryrun or args.force):
    args.force = stagingcontrol.prompt_for_confirmation(args)

if args.verbose:
    print "Instance   : Status"

for instance in actionlist:
    inst_running = instance.state
    if args.start and not (u'running' == inst_running or u'pending' == inst_running):
        if args.dryrun:
            print "DRYRUN: start up {0}".format(instance.id)
        else:
            try:
                instance.start()
            except EC2ResponseError as e:
                if not args.quiet:
                    print "Error starting {0}: {1}".format(instance.id, e.error_message)
                continue
            if not args.quiet:
                print '{0} : {1}'.format(instance.id, 'pending')
    elif args.stop and (u'running' == inst_running) and not (u'stopping' == inst_running):
        if args.dryrun:
            print "DRYRUN: stopping {0}".format(instance.id)
        else:
            try:
                instance.stop()
            except EC2ResponseError as e:
                if not args.quiet:
                    print "Error stopping {0}: {1}".format(instance.id, e.error_message)
                continue
            if not args.quiet:
                print '{0} : {1}'.format(instance.id, 'stopping')
    elif u'pending' == inst_running:
        if not args.quiet:
            print '{0} : {1}'.format(instance.id, inst_running)
    elif args.check:
        print '{0} : {1}'.format(instance.id, inst_running)
