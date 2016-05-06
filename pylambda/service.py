# -*- coding: utf-8 -*-
import boto.elastictranscoder
from boto.s3.connection import S3Connection
import json
import boto.ses

pipeline_id = '1451458179766-qniixd'
region = 'ap-northeast-1'
s3conn = S3Connection()
transcoder_client = boto.elastictranscoder.connect_to_region(region)
logstr = ''
srcNotVideoType = ['.png','.jpg','.m3u8','.txt']
srcVideoType = ['.mp4','.mkv']

class NoError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class MyError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def sendemail(subject,data):
    sesconn = boto.ses.connect_to_region('us-west-2')

    email_from = 'janreyho@gmail.com'
    email_to = ['hejiayi@gochinatv.com','zhixueyong@gochinatv.com']

    response = sesconn.send_email(email_from,subject,data,email_to)

    print response

def procKeyName(event,bucket,video,key):
    global logstr
    if key.name.endswith('/'):
        raise NoError("abc")
    for type in srcNotVideoType:
        if key.name.endswith(type):
            raise NoError(type)
    pos = 0
    for type in srcVideoType:
        pos += 1
        if key.name.endswith(type):
            break
        elif len(srcVideoType) == pos:
            raise MyError("not "+str(srcVideoType))

    num1=key.name.rfind('/',0,len(key.name))
    num2=key.name.rfind('.',0,len(key.name))
    output_key = key.name[num1+1:num2]
    if 0 == len(output_key):
        raise NoError(".")

    keypath = key.name[0:num1+1]
    if event.get('src').endswith('/'):
        keyoutpath = keypath.replace(event.get('src'),event.get('dst'),1)
    else:
        keyoutpath = event.get('dst')

    video['src'] = key.name
    if "m3u8" == event.get('type'):
        findkey = keyoutpath + output_key + '_' + event.get('time') +'/'+ output_key +'.m3u8'
    elif "mp4" == event.get('type'):
        findkey = keyoutpath + output_key + '_' + event.get('time') +'/'+ output_key +'.mp4'
    else:
        raise MyError( "not mp4 or m3u8 ")

    video['dst'] = findkey
    logstr += findkey+'\n'
    if bucket.get_key(findkey):
        video['status'] = "exist"
        raise MyError("exist")
    else:
        video['status'] = "transcode"

    video['output_key'] = output_key
    video['keyoutpath'] = keyoutpath
    # print keyoutpath

def produceHLS(event,job,video,key):
    hls_0800k_mypreset_id     = '1461232174018-5qze1a';
    hls_1600k_mypreset_id     = '1461232247133-cktkzt';
    hls_2500k_mypreset_id     = '1461232297177-cda2ts';
    hls_4000k_mypreset_id     = '1461232343088-ow0pfo';
    # Setup the job input using the provided input key.
    segment_duration = '6'

    hls_0800k = {
        'Key' : 'hls0800k/' + video['output_key'],
        'PresetId' : hls_0800k_mypreset_id,
        'SegmentDuration' : segment_duration,
        'ThumbnailPattern' : '{count}'
    }
    hls_1600k = {
        'Key' : 'hls1600k/' + video['output_key'],
        'PresetId' : hls_1600k_mypreset_id,
        'SegmentDuration' : segment_duration,
    }
    hls_2500k = {
        'Key' : 'hls2500k/' + video['output_key'],
        'PresetId' : hls_2500k_mypreset_id,
        'SegmentDuration' : segment_duration,
    }
    hls_4000k = {
        'Key' : 'hls4000k/' + video['output_key'],
        'PresetId' : hls_4000k_mypreset_id,
        'SegmentDuration' : segment_duration,
    }
    #
    # duration = para['ffprobe']['streams'][0]['duration']
    # coded_height = para['ffprobe']['streams'][para['vstream_index']]['coded_height']
    # bit_rate = int(para['ffprobe']['format']['bit_rate'])
    # if 600 > duration:
    #     thumbnailInterval = 5
    # elif 1800 > duration:
    #     thumbnailInterval = 10
    # else:
    #     thumbnailInterval = 30

    if 480 == event.get('v_height'):
        job_outputs = [ hls_0800k]
    elif 720 == event.get('v_height'):
        if 1200000 > event.get('v_bitrate'):
            job_outputs = [ hls_0800k]
        else:
            job_outputs = [ hls_0800k,hls_1600k]
    elif 1080 == event.get('v_height'):
        if 1200000 > event.get('v_bitrate'):
            job_outputs = [ hls_0800k]
        elif 2000000 > event.get('v_bitrate'):
            job_outputs = [ hls_0800k,hls_1600k]
        elif 4000000 > event.get('v_bitrate'):
            job_outputs = [ hls_0800k,hls_1600k,hls_2500k]
        else:
            job_outputs = [ hls_0800k,hls_1600k,hls_2500k,hls_4000k]
    else:
        raise MyError('not 480p 720p 1080p')

    # Setup master playlist which can be used to play using adaptive bitrate.
    playlist = {
        'Name' : video['output_key'],
        'Format' : 'HLSv3',
        'OutputKeys' : map(lambda x: x['Key'], job_outputs)
    }

    # Creating the job.
    job_input = { 'Key': key.name }
    create_job_request = {
        'pipeline_id' : pipeline_id,
        'input_name' : job_input,
        'output_key_prefix' : video['keyoutpath'] + video['output_key'] + '_' + event.get('time') +'/',
        'outputs' : job_outputs,
        'playlists' : [ playlist ]
    }
    job['create_job_request'] = create_job_request

def produceMP4(event,job,video,key):
    mp4_2000k_mypreset_id     = '1461232916166-ssar47';
    mp4_4000k_mypreset_id     = '1461232828658-w31bg8';

    mp4_2000k = {
        'Key' : video['output_key']+".mp4",
        'PresetId' : mp4_2000k_mypreset_id,
    }
    mp4_4000k = {
        'Key' : video['output_key']+".mp4",
        'PresetId' : mp4_4000k_mypreset_id,
    }

    if 720 == event.get('v_height'):
        if 2000000 > event.get('v_bitrate'):
            raise MyError('720p bitrate<2M')
        else:
            job_outputs = [ mp4_2000k]
    elif 1088 == event.get('v_height'):
        if 4000000 > event.get('v_bitrate'):
            raise MyError('7080p bitrate<4M')
        else:
            job_outputs = [ mp4_4000k]
    else:
        raise MyError('not 720p or 1080p')

    # Creating the job.
    job_input = { 'Key': key.name }
    create_job_request = {
        'pipeline_id' : pipeline_id,
        'input_name' : job_input,
        'output_key_prefix' : video['keyoutpath'] + video['output_key'] + '_' + event.get('time') +'/',
        'outputs' : job_outputs,
        # 'playlists' : [ para['playlist']]
    }
    job['create_job_request'] = create_job_request

def handler(event, context):
    out = {}
    out['videos'] = []

    bucket = s3conn.get_bucket(event.get('bucket'))
    print 'hejiayi1'

    for key in bucket.list(event.get('src'),''):
        video = {}
        job = {}
        try:
            procKeyName(event,bucket,video,key)
            # ffprobeJson(para,key)
            if 'mp4' == event.get('type'):
                produceMP4(event,job,video,key)
            elif 'm3u8' == event.get('type'):
                produceHLS(event,job,video,key)
            else:
                raise MyError( "2 not mp4 or m3u8 ")

            if "no" != event.get('testflag'):
                raise MyError( "test")

            video['error'] = "no"
            create_job_result=transcoder_client.create_job(**job['create_job_request'])

        except MyError as e:
            video['error'] = e.value
            out['videos'].append(video)
        except NoError as e:
            pass
        else:
            out['videos'].append(video)

    data = json.dumps(out)
    sendemail('lambdaTranscoder',logstr+data)
    return data
