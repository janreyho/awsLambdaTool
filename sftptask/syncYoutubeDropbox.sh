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

		# filetime=`stat -c %Y $1/$file1`
		# now=`date +%s`

		# if [ ! -f $3 ];then
		# 	sudo touch /home/yangshiwuxi/log/$3
		# 	sudo chmod 777 /home/yangshiwuxi/log/$3
		# fi

		if [ -d $1/$file -a -f $1/$file1/delivery.complete ];then
			echo "mv $1/$file1 $2"
			sudo mkdir $2/$file1
			sudo find $1/$file1 -not -name delivery.complete -type f -print -exec mv {} $2/$file1/ \;
			sudo mv $1/$file1/delivery.complete $2/$file1
			sudo rmdir $1/$file1
			sudo touch /home/yangshiwuxi/log/delivery.complete
		fi
	done
}

fun $1 $2 $3

sudo umount /mnt/dropbox
