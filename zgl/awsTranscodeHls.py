# -*- coding: utf-8 -*-
#!/usr/bin/python
import sys
import hashlib
import json
import sys
import getopt
import os
import commands

import boto.elastictranscoder
from boto.s3.connection import S3Connection

# This is the ID of the Elastic Transcoder pipeline that was created when
# setting up your AWS environment:
# http://docs.aws.amazon.com/elastictranscoder/latest/developerguide/sample-code.html#python-pipeline



def usage():
  print "use:python *.py -u time -b bucket -f (file|folder) -i src -o dst -t test"
  sys.exit()

opts, args = getopt.getopt(sys.argv[1:], "hb:u:f:i:o:t:")
bucket=""
src=""
dst=""
TEST=""
fileflag=""
time=""

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
    elif op == "-u":
        time = value
    elif op == "-h":
        usage()

num = len(sys.argv)
if 13 != num:
  print "error para num="+str(num)
  usage()
  sys.exit()

print "bucket:" +bucket
print "src:" +src
print "dst:" +dst
print "time:" +time

# os.system('ls .') 
# os.system('touch hejiayi') 
# sys.exit()

pipeline_id = '1451458179766-qniixd'
region = 'ap-northeast-1'
segment_duration = '6'
#All outputs will have this prefix prepended to their output key.
# input_key_prefix = 'zhongguolan/videos/src/'
# thumbnail_pattern = 'thumbnail{count}'
# HLS Presets that will be used to create an adaptive bitrate playlist.

hls_0800k_mypreset_id     = '1460467985190-1cxhbu';
hls_1600k_mypreset_id     = '1460468139207-wxacbb';
hls_atuo_mypreset_id     = '1460517949509-5owzfo';
# hls_4001k_mypreset_id     = '1453104062613-gblgt0';
# Creating client for accessing elastic transcoder
transcoder_client = boto.elastictranscoder.connect_to_region(region)


conn = S3Connection()
bucket = conn.get_bucket(bucket)

file_object = open('resolution.txt', 'w')
file_transcode = open('transcode.txt', 'w')
for key in bucket.list(src,''):
    # print key.name
    num1=key.name.rfind('/',0,len(key.name))
    num2=key.name.rfind('.',0,len(key.name))
    filetype = key.name[num2:len(key.name)]

    if '.mp4'!=filetype:
        continue

    output_key = key.name[num1+1:num2]
    output_path = output_key + '_' + time
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


    findkey = keyoutpath + output_path +'/'+ output_key +'.m3u8'
    print "findkey:"+findkey
    if bucket.get_key(findkey):
        print '****exist:'+findkey
        continue

    print '####transcode:' + output_key
    print keyoutpath

    # Setup the job input using the provided input key.
    job_input = { 'Key': key.name }

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
    hls_auto = {
        'Key' : 'hls_auto/' + output_key,
        'PresetId' : hls_atuo_mypreset_id,
        'SegmentDuration' : segment_duration,
        'ThumbnailPattern' : '{count}'
    }


    # job_outputs = [ hls_400k,hls_0800k, hls_1600k, hls_2500k, hls_4001k]
    

    a,b = commands.getstatusoutput('ffprobe -v quiet -print_format json -show_format -show_streams /mnt/s3/' + key.name)
    c = json.loads(b)
    file_object.write(str(c['format']['bit_rate'])+'\t\t')
    file_object.write(str(c['streams'][0]['coded_width'])+'*'+str(c['streams'][0]['coded_height'])+'\t\t')
    file_object.write(key.name + '\n')

    if 480 == c['streams'][0]['coded_height']:
        job_outputs = [ hls_auto]
    elif 720 == c['streams'][0]['coded_height']:
        if 1200000 > int(c['format']['bit_rate']):
            job_outputs = [ hls_auto]
        else:
            job_outputs = [ hls_auto,hls_0800k]
    elif 1088 == c['streams'][0]['coded_height']:
        if 1200000 > int(c['format']['bit_rate']):
            job_outputs = [ hls_auto]
        elif 2000000 > int(c['format']['bit_rate']):
            job_outputs = [ hls_auto,hls_0800k]
        else:
            job_outputs = [ hls_auto,hls_0800k,hls_1600k]
    else:
        file_object.write('ERROR:coded_height:' + key.name + '\n')

    file_object.write(str(job_outputs)+ '\n')
 
    if "no" != TEST:
        continue

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
        'output_key_prefix' : keyoutpath + output_path +'/',
        'outputs' : job_outputs,
        'playlists' : [ playlist ]
    }

    # print json.dumps(create_job_request)

    create_job_result=transcoder_client.create_job(**create_job_request)

    file_transcode.write('transcoded:' +output_key)
    file_transcode.write(json.dumps(create_job_result['Job'], indent=4, sort_keys=True))
    # print 'HLS job has been created: ', json.dumps(create_job_result['Job'], indent=4, sort_keys=True)

file_object.close()
file_transcode.close()
