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
# python awsTranscode.py -u 20160413000001 -b ottcloud -c publicspace -f folder -i zhongguolan/videos/src -o publicspace/videos/dst -t test > work.log 2>&1 &

def usage():
  print "use:python *.py -u time -b bucket -c cp -f (file|folder) -s src -d dst -t test"
  sys.exit()

def onSIGINT(a,b):
    print 'recv SIGINT'
    file_object.close()
    file_transcode.close()
    os._exit()

def procpara(para):
    opts, args = getopt.getopt(sys.argv[1:], "hu:b:c:f:s:d:t:")
    print sys.argv
    num = len(sys.argv)
    if 15 != num:
        print "error para num="+str(num)
        usage()
        sys.exit()

    for op, value in opts:
        if op == "-b":
            para['-b'] = value
        elif op == "-s":
            para['-s'] = value
        elif op == "-d":
            para['-d'] = value
        elif op == "-t":
            para['-t'] = value
        elif op == "-f":
            para['-f'] = value
        elif op == "-u":
            para['-u'] = value
        elif op == "-c":
            para['-c'] = value
        elif op == "-h":
            usage()




def procKeyName(para,key):
    if not key.name.endswith(".mp4"):
        return 1

    num1=key.name.rfind('/',0,len(key.name))
    num2=key.name.rfind('.',0,len(key.name))
    output_key = key.name[num1+1:num2]
    if 0 == len(output_key):
        return 1

    keypath = key.name[0:num1+1]

    if "file" == para['-f']:
        keyoutpath = para['-d']
    elif "folder" == para['-f']:
        keyoutpath = keypath.replace(para['-s'],para['-d'],1)
    else:
        print "error: not file or folder"
        sys.exit()


    findkey1 = keyoutpath + output_key + '_' + para['-u'] +'/'+ output_key +'.m3u8'
    findkey2 = keyoutpath + output_key + '_' + para['-u'] +'/'+ output_key +'.mp4'
    if bucket.get_key(findkey1):
        print '****exist m3u8:'+findkey1
        return 1
    elif  bucket.get_key(findkey2):
        print '****exist mp4:'+findkey2
        return 1
    print '####transcode:' + key.name
    para['output_key'] = output_key
    para['keyoutpath'] = keyoutpath
    print keyoutpath


def ffprobeJson(para,key):
    a,b = commands.getstatusoutput('/usr/local/bin/ffprobe -v quiet -print_format json -show_format -show_streams /mnt/s3/' + key.name)
    c = json.loads(b)
    file_object.write(str(c['format']['bit_rate'])+'\t\t')
    file_object.write(str(c['streams'][0]['coded_width'])+'*'+str(c['streams'][0]['coded_height'])+'\t\t')
    file_object.write(str(c['format']['size'])+'\t\t')
    file_object.write(str(c['format']['duration'])+'\t\t')
    file_object.write(key.name + '\n')
    para['ffprobe'] = c

def produceHLS(para,key):
    hls_0800k_mypreset_id     = '1461232174018-5qze1a';
    hls_1600k_mypreset_id     = '1461232247133-cktkzt';
    hls_2500k_mypreset_id     = '1461232297177-cda2ts';
    hls_4000k_mypreset_id     = '1461232343088-ow0pfo';
    # Setup the job input using the provided input key.
    segment_duration = '6'

    hls_0800k = {
        'Key' : 'hls0800k/' + para['output_key'],
        'PresetId' : hls_0800k_mypreset_id,
        'SegmentDuration' : segment_duration,
        'ThumbnailPattern' : '{count}'
    }
    hls_1600k = {
        'Key' : 'hls1600k/' + para['output_key'],
        'PresetId' : hls_1600k_mypreset_id,
        'SegmentDuration' : segment_duration,
    }
    hls_2500k = {
        'Key' : 'hls2500k/' + para['output_key'],
        'PresetId' : hls_2500k_mypreset_id,
        'SegmentDuration' : segment_duration,
    }
    hls_4000k = {
        'Key' : 'hls4000k/' + para['output_key'],
        'PresetId' : hls_4000k_mypreset_id,
        'SegmentDuration' : segment_duration,
    }

    if 600 > para['ffprobe']['streams'][0]['duration']:
        thumbnailInterval = 5
    elif 1800 > para['ffprobe']['streams'][0]['duration']:
        thumbnailInterval = 10
    else:
        thumbnailInterval = 30

    if 480 == para['ffprobe']['streams'][0]['coded_height']:
        job_outputs = [ hls_0800k]
    elif 720 == para['ffprobe']['streams'][0]['coded_height']:
        if 1200000 > int(para['ffprobe']['format']['bit_rate']):
            job_outputs = [ hls_0800k]
        else:
            job_outputs = [ hls_0800k,hls_1600k]
    elif 1088 == para['ffprobe']['streams'][0]['coded_height']:
        if 1200000 > int(para['ffprobe']['format']['bit_rate']):
            job_outputs = [ hls_0800k]
        elif 2000000 > int(para['ffprobe']['format']['bit_rate']):
            job_outputs = [ hls_0800k,hls_1600k]
        elif 4000000 > int(para['ffprobe']['format']['bit_rate']):
            job_outputs = [ hls_0800k,hls_1600k,hls_2500k]
        else:
            job_outputs = [ hls_0800k,hls_1600k,hls_2500k,hls_4000k]
    else:
        file_object.write('ERROR:coded_height:' + key.name + '\n')

    file_object.write(str(job_outputs)+ '\n')

    # Setup master playlist which can be used to play using adaptive bitrate.
    playlist = {
        'Name' : para['output_key'],
        'Format' : 'HLSv3',
        'OutputKeys' : map(lambda x: x['Key'], job_outputs)
    }

    # Creating the job.
    job_input = { 'Key': key.name }
    create_job_request = {
        'pipeline_id' : pipeline_id,
        'input_name' : job_input,
        'output_key_prefix' : para['keyoutpath'] + para['output_key'] + '_' + para['-u'] +'/',
        'outputs' : job_outputs,
        'playlists' : [ playlist ]
    }

    para['create_job_request'] = create_job_request

def produceMP4(para,key):
    mp4_2000k_mypreset_id     = '1461232916166-ssar47';
    mp4_4000k_mypreset_id     = '1461232828658-w31bg8';

    hls_2000k = {
        'Key' : para['output_key']+".mp4",
        'PresetId' : mp4_2000k_mypreset_id,
    }
    hls_4000k = {
        'Key' : para['output_key']+".mp4",
        'PresetId' : mp4_4000k_mypreset_id,
    }

    if 720 == para['ffprobe']['streams'][0]['coded_height']:
        if 2000000 > int(para['ffprobe']['format']['bit_rate']):
            file_object.write('ERROR:720p bitrate<2M:' + key.name + '\n')
        else:
            job_outputs = [ hls_2000k]
    elif 1088 == para['ffprobe']['streams'][0]['coded_height']:
        if 4000000 > int(para['ffprobe']['format']['bit_rate']):
            file_object.write('ERROR:1080p bitrate<4M:' + key.name + '\n')
        else:
            job_outputs = [ hls_4000k]
    else:
        file_object.write('ERROR:not 720p or 1080p:' + key.name + '\n')
    file_object.write(str(job_outputs)+ '\n')

    # Creating the job.
    job_input = { 'Key': key.name }
    create_job_request = {
        'pipeline_id' : pipeline_id,
        'input_name' : job_input,
        'output_key_prefix' : para['keyoutpath'] + para['output_key'] + '_' + para['-u'] +'/',
        'outputs' : job_outputs,
        # 'playlists' : [ para['playlist']]
    }

    para['create_job_request'] = create_job_request


if __name__ == '__main__':
    para={}
    procpara(para)

    pipeline_id = '1451458179766-qniixd'
    region = 'ap-northeast-1'

    transcoder_client = boto.elastictranscoder.connect_to_region(region)
    conn = S3Connection()
    bucket = conn.get_bucket(para['-b'])

    file_object = open('/gochina/'+para['-c']+'/log/resolution_'+para['-u']+'.txt', 'w')
    file_transcode = open('/gochina/'+para['-c']+'/log/transcode_'+para['-u']+'.txt', 'w')

    signal.signal(signal.SIGINT,onSIGINT)

    for key in bucket.list(para['-s'],''):

        if 1 == procKeyName(para,key):
            continue

        ffprobeJson(para,key)

        if "publicspace" == para['-c']:
            if 1 == produceMP4(para,key):
                continue
        else:
            if 1 == produceHLS(para,key):
                continue

        # print json.dumps(para)


        if "no" != para['-t']:
            continue

        create_job_result=transcoder_client.create_job(**para['create_job_request'])

        file_transcode.write('transcoded:' +para['output_key'])
        file_transcode.write(json.dumps(create_job_result['Job'], indent=4, sort_keys=True))
        # print 'HLS job has been created: ', json.dumps(create_job_result['Job'], indent=4, sort_keys=True)
        # print hejiayi

    file_object.close()
    file_transcode.close()
