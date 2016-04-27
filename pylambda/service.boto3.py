# -*- coding: utf-8 -*-
import boto3
import json

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

def procKeyName(event,para,video,key):
    if key.name.endswith('/'):
        raise NoError("abc")
    if key.name.endswith('.png'):
        raise NoError(".png")
    if not key.name.endswith('.mp4'):
        raise MyError("Suffix must is .mp4")

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
        raise MyError( "type must is  mp4 or m3u8, but it is "+event.get('type'))

    video['dst'] = findkey
    print "  :"+findkey
    if para['bucket'].get_key(findkey):
        video['status'] = "exist"
    else:
        video['status'] = "transcode"
    video['output_key'] = output_key
    video['keyoutpath'] = keyoutpath
    print keyoutpath

def handler(event, context):
    para={}
    out = {}
    out['videos'] = []


    print 'hejiayi1'
    pipeline_id = '1451458179766-qniixd'
    region = 'ap-northeast-1'

    s3 = boto3.client('s3')
    # s3 = boto3.resource('s3')
    # bucket = s3.Bucket(event.get('bucket'))

    # client_transcoder = boto3.client('elastictranscoder')

    # transcoder_client = boto.elastictranscoder.connect_to_region(region)
    # conn = S3Connection()
    # bucket = conn.get_bucket(event.get('bucket'))
    # para['bucket'] = bucket

    print event.get('bucket')
    print event.get('src')

    obj = s3.list_objects(Bucket=event.get('bucket'),Prefix=event.get('src'))
    print json.dumps(obj)
    print obj['Prefix']

    for obj in s3.list_objects(Bucket=event.get('bucket'),Prefix=event.get('src')):
        print 'hjy'
        print obj
        video = {}
        try:
            print obj['Prefix']
            if 1 == procKeyName(event,para,video,obj):
                continue

        except MyError as e:
            video['error'] = e.value
            out['videos'].append(video)
        except NoError as e:
            pass
        else:
            out['videos'].append(video)


    return json.dumps(out)
