#!/usr/bin/env python

import boto
import ConfigParser
import sys

class ServerList(object):
    """
    ServerList
    ==========

    This class parses and validates a list of instance IDs.

    Any invalid IDs get moved in the list automatically, to a non-actioned section.


    Assumptions
    -----------
    The instance IDs listed in the instancelist file are all
    staging/UAT/development machines, expected to be powered
    off and on automatically.


    Format of instancelist
    ----------------------
    The file with the instance IDs must be a normal config file,
    in the .ini style. The script expects (by default) the section
    "[Staging]" (no quotes) to be present, with a list of instance IDs
    underneath this. An example:

    instancelist example
    --------------------
    [Staging]
    i-1b3456
    i-234c34
    """
    def __init__(self, listname, ec2connection):
        """(ServerList, str, boto.ec2.connection.EC2Connection) -> ServerList

        Accepts a `str` for the list name's full or relative filesystem location
        and an already established `EC2Connection`.
        """
        self.listname = listname
        self.conn = ec2connection
        try:
            listfileh = open(self.listname)
        except IOError as e:
            print "Error opening {0}: {1}".format(self.listname,e.strerror)
            sys.exit(1)
        self.config = ConfigParser.ConfigParser(allow_no_value=True)
        self.config.readfp(listfileh)
        listfileh.close()

    def save(self, dryrun=False):
        """(ServerList, bool) -> NoneType

        Save the list from memory to disk"""
        if dryrun:
            print "DRYRUN: Save the instance list to disk"
        else:
            listfh = open(self.listname,'w') #TODO: add exception handling
            self.config.write(listfh)
            listfh.close()


    def parse(self, section='Staging'):
        """(ServerList, str) -> list of EC2 instances

        Validate that the section of the list has EBS-backed instances
        Move non-EBS-backed instances to another section of the list
        Move instances that are not in ec2 to another section of the list
        Return a list of ec2 instances"""
        retlist = []

        if not self.config.has_section(section):
            return retlist

        if not self.config.has_section('Non-EBS'):
            self.config.add_section('Non-EBS')

        if not self.config.has_section('Not Found'):
            self.config.add_section('Not Found')

        for server in self.config.items(section):
            server = server[0]
            try:
                srvinfo = self.conn.get_all_instances(instance_ids=[server])
            except boto.exception.EC2ResponseError:
                srvinfo = None
            if srvinfo == None:
                self.config.set('Not Found',server,None)
                self.config.remove_option(section,server)
            else:
                for inst in srvinfo[0].instances:
                    if u'ebs' == inst.root_device_type:
                        if u'terminated' == inst.state:
                            self.config.set('Not Found',server,None)
                            self.config.remove_option(section,server)
                        else:
                            retlist.append(inst)
                    else:
                        self.config.set('Non-EBS',server,None)
                        self.config.remove_option(section,server)

        return retlist

