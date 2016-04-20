# -*- coding: utf-8 -*-
#!/usr/bin/python
import sys
import hashlib
import json
import sys
import getopt
import os
import commands
import signal

import boto.elastictranscoder
from boto.s3.connection import S3Connection

# This is the ID of the Elastic Transcoder pipeline that was created when
# setting up your AWS environment:
# http://docs.aws.amazon.com/elastictranscoder/latest/developerguide/sample-code.html#python-pipeline



def usage():
  print "use:python *.py -u time -b bucket -c cp -f (file|folder) -i src -o dst -t test"
  sys.exit()

opts, args = getopt.getopt(sys.argv[1:], "hb:c:u:f:i:o:t:")
bucket=""
src=""
dst=""
TEST=""
fileflag=""
time=""
contProv=""

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
    elif op == "-c":
        contProv = value
    elif op == "-h":
        usage()

num = len(sys.argv)
if 15 != num:
  print "error para num="+str(num)
  usage()
  sys.exit()

print "bucket:" +bucket
print "src:" +src
print "dst:" +dst
print "time:" +time


pipeline_id = '1451458179766-qniixd'
region = 'ap-northeast-1'
segment_duration = '6'
#All outputs will have this prefix prepended to their output key.
# input_key_prefix = 'zhongguolan/videos/src/'
# thumbnail_pattern = 'thumbnail{count}'
# HLS Presets that will be used to create an adaptive bitrate playlist.

hls_0800k_mypreset_id     = '1460610438702-plue8g';
hls_1600k_mypreset_id     = '1460468139207-wxacbb';
hls_2500k_mypreset_id     = '1460468427582-73dwrb';
hls_4000k_mypreset_id     = '1460605160645-eeynb5';
# Creating client for accessing elastic transcoder
transcoder_client = boto.elastictranscoder.connect_to_region(region)


conn = S3Connection()
bucket = conn.get_bucket(bucket)

file_object = open('/home/ubuntu/gochina/'+contProv+'/log/resolution_'+time+'.txt', 'w')
file_transcode = open('/home/ubuntu/gochina/'+contProv+'/log/transcode_'+time+'.txt', 'w')

def onSIGINT(a,b):
    print 'recv SIGINT'
    file_object.close()
    file_transcode.close()
    os._exit()
    # sys.exit()

signal.signal(signal.SIGINT,onSIGINT)

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
        'ThumbnailPattern' : '{count}'
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
    hls_4000k = {
        'Key' : 'hls4000k/' + output_key,
        'PresetId' : hls_4000k_mypreset_id,
        'SegmentDuration' : segment_duration,
    }


    a,b = commands.getstatusoutput('ffprobe -v quiet -print_format json -show_format -show_streams /mnt/s3/' + key.name)
    c = json.loads(b)
    file_object.write(str(c['format']['bit_rate'])+'\t\t')
    file_object.write(str(c['streams'][0]['coded_width'])+'*'+str(c['streams'][0]['coded_height'])+'\t\t')
    file_object.write(key.name + '\n')

    if 600 > c['streams'][0]['duration']:
        thumbnailInterval = 5
    elif 1800 > c['streams'][0]['duration']:
        thumbnailInterval = 10
    else:
        thumbnailInterval = 30

    if 480 == c['streams'][0]['coded_height']:
        job_outputs = [ hls_0800k]
    elif 720 == c['streams'][0]['coded_height']:
        if 1200000 > int(c['format']['bit_rate']):
            job_outputs = [ hls_0800k]
        else:
            job_outputs = [ hls_0800k,hls_1600k]
    elif 1088 == c['streams'][0]['coded_height']:
        if 1200000 > int(c['format']['bit_rate']):
            job_outputs = [ hls_0800k]
        elif 2000000 > int(c['format']['bit_rate']):
            job_outputs = [ hls_0800k,hls_1600k]
        elif 4000000 > int(c['format']['bit_rate']):
            job_outputs = [ hls_0800k,hls_1600k,hls_2500k]
        else:
            job_outputs = [ hls_0800k,hls_1600k,hls_2500k,hls_4000k]
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
