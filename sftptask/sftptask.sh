#!/bin/bash
ps -fe | grep "/gochina/sftptask/syncYoutubeDropbox.sh" | grep -v grep
if [ $? -eq 0 ]; then
	exit 0
fi

var=` TZ='Asia/Shanghai' date +%Y%m%d%H%M%S `
echo $var
echo "hjy1"
sudo /gochina/sftptask/syncYoutubeDropbox.sh /sftp_users/yangshiwuxi /mnt/dropbox $var >> /home/yangshiwuxi/log/$var 2>&1
sudo /gochina/sftptask/syncS3.sh /sftp_users/devtest /mnt/s3/sftpupload/devtest $var >> /home/devtest/log/$var 2>&1

