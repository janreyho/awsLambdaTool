#!/bin/bash

sudo sshfs yt-gochinatv@partnerupload.google.com:/ /mnt/dropbox/ -o IdentityFile=/home/ubuntu/.ssh/cms-jynrb.pem -p 19321

function fun(){

	if [ "ls" == $1 ];then
		sudo ls /mnt/dropbox
		return
	fi

	if [ "mount" == $1 ];then
		exit
	fi

	if [ "df" == $1 ];then
		sudo df -h
		return
	fi

	for file1 in ` ls $1 `
	do
		echo $file1

		filetime=`stat -c %Y $1/$file1`
		now=`date +%s`

		if [ ! -f $3 ];then
			sudo touch /home/yangshiwuxi/log/$3
			sudo chmod 777 /home/yangshiwuxi/log/$3
		fi

		if [ $[ $now - $filetime ] -gt 60 ];then
			echo "mv $1/$file1 $2"
			sudo echo "mv $1/$file1 $2" >> /home/yangshiwuxi/log/$3
			sudo mv $1/$file1 $2/
		fi
	done
}

fun $1 $2 $3

sudo umount /mnt/dropbox
