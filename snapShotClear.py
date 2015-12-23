#!/usr/bin/env python27

import ntpath
import hashlib
import os, glob, shutil, sys
import os.path
from os import stat
from pwd import getpwnam
from pwd import getpwuid
from grp import getgrnam
import subprocess
import zipfile
import base64
import struct
import subprocess
import yaml
from yaml import load, dump

import boto.ec2


from datetime import datetime, date, timedelta
from dateutil import parser
from pprint import pprint
import time
import traceback
import re



region=''
days=14
#keyaccess={{keyaccess}}
#keysecret={{keysecret}}
#s3mount={{s3mount}}

class generic(object):
        def __init__(self, *initial_data, **kwargs):
                for dictionary in initial_data:
                        for key in dictionary:
                                setattr(self,key,dictionary[key])
                        for key in kwargs:
                                setattr(self, key, kwargs[key])



def writeToFile(pathandfile, inputmessagestr):
    stream = open(pathandfile, 'w')
    stream.write(inputmessagestr)
    stream.close()

def getAWSCredentials():
    pathtoaws = '/home/www-data/.aws/credentials'
    with open(pathtoaws) as f:
        for line in f:
            if "aws_access_key_id" in line:
                awskey = line.replace("aws_access_key_id=", "")
                awskey = awskey.replace("\n", "")
                # print '   aws_access_key_id: %s'%(awskey)
            if "aws_secret_access_key" in line:
                awssecretkey = line.replace("aws_secret_access_key=", "")
                awssecretkey = awssecretkey.replace("\n", "")
                # print '   aws_secret_access_key: %s'%(awssecretkey)

    output = [awskey, awssecretkey]
    return output


class VolumeCleaner():
        def main(self):
            #import boto3  snap-46959572
            awscredent = getAWSCredentials()
            aws_key=awscredent[0]
            aws_secret=awscredent[1]
            ec2 = boto.ec2.connect_to_region(region,aws_access_key_id=aws_key, aws_secret_access_key=aws_secret)
            self.deleteByVolumes(ec2)
            self.deleteBySnapShots(ec2)

        def deleteBySnapShots(self,ec2):
            print "delete by snapshots!!"
            snapshots = ec2.get_all_snapshots()
            limit = datetime.now() - timedelta(days=days)
            aSnaps = ['snap-af8ef847','snap-a28ef84a']
            snap_sorted = sorted([(s.id, s.start_time) for s in snapshots], key=lambda k: k[1])
            for s in snap_sorted:
                if (s[0] in aSnaps):
                    continue
                if parser.parse(s[1]).date() <= limit.date():
                    try:
                        ec2.delete_snapshot(s[0])
                        print s[0]
                        print "[D]2 deleting ...date of snapshot::", s[1]
                    except Exception, e:
                        if ("InvalidSnapshot.NotFound" in str(e)):
                            continue
                        print "[E]2 failed-->%s  id:%s date:%s"%(e,s[0],s[1])

        def deleteByVolumes(self,ec2):
            volumes = ec2.get_all_volumes()
            limit = datetime.now() - timedelta(days=days)
            aSnaps = ['snap-af8ef847','snap-a28ef84a']
            for v in volumes:
                snapshots = v.snapshots()
                snap_sorted = sorted([(s.id, s.start_time) for s in snapshots], key=lambda k: k[1])
                #for s in snap_sorted[ :-4] :
                for s in snap_sorted:
                    if (s[0] in aSnaps):
                        continue
                    if parser.parse(s[1]).date() <= limit.date():
                        try:
                            ec2.delete_snapshot(s[0])
                            print s[0]
                            print "[D] deleting...date of snapshot::", s[1]
                        except Exception, e:
                            if ("InvalidSnapshot.NotFound" in str(e)):
                                continue
                            print "[E]failed-->%s  id:%s date:%s"%(e,s[0],s[1])



prompt = sys.argv[1]

if 'help' in prompt:
        print "used to clear snapshots that are older than ndays"
        print "python27 snapShotClear.py region,days-Old"
        ## 'ap-southeast-2'  'us-west-1'
else:
        values = prompt.split(',')
        region = str(values[0])  #//  'zip'  'restore'
        if len(region)<7:
                region = 'us-west-2'
        elif ' ' in region:
                region= 'us-west-2'
        print region
        #get optional variables
        try:
            days = str(values[1])
        except:
            print "[W] days back not provided defaulting to 14 days"
            days = 14
        check = VolumeCleaner()
        check.main()
