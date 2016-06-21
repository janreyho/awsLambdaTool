#!/bin/bash

var=` TZ='Asia/Shanghai' date +%Y%m%d%H%M%S `
echo $var

function fun(){

	for file1 in ` ls $1 `
	do
		filetime=`stat -c %Y $1/$file1`
		now=`date +%s`
		if [ $[ $now - $filetime ] -gt 300 ];then 
			sudo mv $1/$file1 $2
		fi
	done 
}

fun $1 $2

