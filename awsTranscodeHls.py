# -*- coding: utf-8 -*-
#!/usr/bin/python
import sys
import hashlib
import json
import sys
import getopt
# import os

import boto.elastictranscoder
from boto.s3.connection import S3Connection

# This is the ID of the Elastic Transcoder pipeline that was created when
# setting up your AWS environment:
# http://docs.aws.amazon.com/elastictranscoder/latest/developerguide/sample-code.html#python-pipeline



def usage():
  print "use:python *.py -b bucket -f (file|folder) -i src -o dst -t test"
  sys.exit()

opts, args = getopt.getopt(sys.argv[1:], "hb:f:i:o:t:")
bucket=""
src=""
dst=""
TEST=""
fileflag=""

for op, value in opts:
    if op == "-b":
        bucket = value
    elif op == "-i":
        src = value
    elif op == "-o":
        dst = value
    elif op == "-t":
        TEST = value
    elif op == "-f":
        fileflag = value
    elif op == "-h":
        usage()

num = len(sys.argv)
if 11 != num:
  print "error para num="+str(num)
  usage()
  sys.exit()

print "bucket:" +bucket
print "src:" +src
print "dst:" +dst


pipeline_id = '1451458179766-qniixd'
region = 'ap-northeast-1'
segment_duration = '2'
#All outputs will have this prefix prepended to their output key.
# input_key_prefix = 'zhongguolan/videos/src/'
# thumbnail_pattern = 'thumbnail{count}'
# HLS Presets that will be used to create an adaptive bitrate playlist.

hls_0400k_preset_id     = '1351620000001-200050';
hls_0800k_mypreset_id     = '1451888005236-hdphcq';
hls_1600k_mypreset_id     = '1451887928494-u9vd2j';
hls_2500k_mypreset_id     = '1451887780433-08sxuj';
hls_4001k_mypreset_id     = '1453104062613-gblgt0';
# Creating client for accessing elastic transcoder
transcoder_client = boto.elastictranscoder.connect_to_region(region)


conn = S3Connection()
bucket = conn.get_bucket(bucket)

# sys.exit()
for key in bucket.list(src,''):
    # print key.name
    num1=key.name.rfind('/',0,len(key.name))
    num2=key.name.rfind('.',0,len(key.name))
    filetype = key.name[num2:len(key.name)]

    if '.mp4'!=filetype:
        continue

    output_key = key.name[num1+1:num2]
    if 0 == len(output_key):
        continue

    keypath = key.name[0:num1+1]

    if "file" == fileflag:
        keyoutpath = keypath.replace(keypath,dst,1)
    elif "folder" == fileflag:
        keyoutpath = keypath.replace(src,dst,1)
    else:
        print "error: not file or folder"
        sys.exit()


    findkey = keyoutpath + output_key +'/'+ output_key +'.m3u8'
    print "findkey:"+findkey
    if bucket.get_key(findkey):
        print '****exist:'+findkey
        continue

    print '####transcode:' + output_key
    print keyoutpath

    if "no" != TEST:
        continue

    # Setup the job input using the provided input key.
    job_input = { 'Key': key.name }

    hls_400k = {
        'Key' : 'hls0400k/' + output_key,
        'PresetId' : hls_0400k_preset_id,
        'SegmentDuration' : segment_duration
    }
    hls_0800k = {
        'Key' : 'hls0800k/' + output_key,
        'PresetId' : hls_0800k_mypreset_id,
        'SegmentDuration' : segment_duration,
    }
    hls_1600k = {
        'Key' : 'hls1600k/' + output_key,
        'PresetId' : hls_1600k_mypreset_id,
        'SegmentDuration' : segment_duration,
    }
    hls_2500k = {
        'Key' : 'hls2500k/' + output_key,
        'PresetId' : hls_2500k_mypreset_id,
        'SegmentDuration' : segment_duration,
    }
    hls_4001k = {
        'Key' : 'hls4001k/' + output_key,
        'PresetId' : hls_4001k_mypreset_id,
        'SegmentDuration' : segment_duration,
        'ThumbnailPattern' : '{count}'
    }

    job_outputs = [ hls_400k,hls_0800k, hls_1600k, hls_2500k, hls_4001k]

    # Setup master playlist which can be used to play using adaptive bitrate.
    playlist = {
        'Name' : output_key,
        'Format' : 'HLSv3',
        'OutputKeys' : map(lambda x: x['Key'], job_outputs)
    }

    # Creating the job.
    create_job_request = {
        'pipeline_id' : pipeline_id,
        'input_name' : job_input,
        'output_key_prefix' : keyoutpath + output_key +'/',
        'outputs' : job_outputs,
        'playlists' : [ playlist ]
    }

    # print json.dumps(create_job_request)

    create_job_result=transcoder_client.create_job(**create_job_request)
    print 'transcoded:' +output_key
    print 'HLS job has been created: ', json.dumps(create_job_result['Job'], indent=4, sort_keys=True)
