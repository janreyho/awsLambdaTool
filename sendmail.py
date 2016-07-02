import sys
import hashlib
import json
import getopt
import os
import commands
import signal
import boto.elastictranscoder
import boto.ses
from boto.s3.connection import S3Connection

def usage():
  print "use:python sendmail.py -s subject -b body"
  sys.exit()

def procpara(para):
    opts, args = getopt.getopt(sys.argv[1:], "hs:b:")
    print sys.argv
    num = len(sys.argv)
    if 5 != num:
        print "error para num="+str(num)
        usage()
        sys.exit()

    for op, value in opts:
        if op == "-b":
            para['-b'] = value
        elif op == "-s":
            para['-s'] = value
        elif op == "-h":
            usage()

def sendemail(subject,data):
    sesconn = boto.ses.connect_to_region('us-west-2')

    email_from = 'janreyho@gmail.com'
    email_to = ['hejiayi@gochinatv.com','zhixueyong@gochinatv.com','lisi@gochinatv.com','panxinming@gochinatv.com','zhangyue@gochinatv.com','caolei@gochinatv.com']

    response = sesconn.send_email(email_from,subject,data,email_to)

    print response

if __name__ == '__main__':
    para={}
    procpara(para)

    print para['-s']
    print para['-b']

    sendemail(para['-s'],para['-b'])

