#!/bin/bash

sudo sshfs yt-gochinatv@partnerupload.google.com:/ /mnt/dropbox/ -o IdentityFile=/home/ubuntu/.ssh/cms-jynrb.pem -p 19321

function fun(){

	if [ "ls" == $1 ];then
		sudo ls /mnt/dropbox
		return
	fi

        if [ "df" == $1 ];then
                sudo df -h
                return
        fi

	for file1 in ` ls $1 `
	do
		filetime=`stat -c %Y $1/$file1`
		now=`date +%s`
		if [ $[ $now - $filetime ] -gt 3600 ];then 
			sudo mv $1/$file1 $2
		fi
	done 
}

fun $1 $2

sudo umount /mnt/dropbox
