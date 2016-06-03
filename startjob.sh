#!/bin/bash
ps -fe | grep "/gochina/gochina/gochinajob.sh $1" | grep -v grep
if [ $? -eq 0 ]; then
	exit 0
fi

var=` TZ='Asia/Shanghai' date +%Y%m%d%H%M%S `
echo $var

for file in ` ls /gochina/gochina/cpconfig `
do
{
	source /gochina/gochina/cpconfig/$file
			/gochina/gochina/gochinajob.sh $1 $file $var >> /gochina/$file/log/$var 2>&1
			echo "/gochina/$file/log/resolution_$var.txt"
			if [ -f /gochina/$file/log/resolution_$var".txt" ]; then
			/usr/bin/mail -s $file'-'$var'更新' $mailrecverstest < /gochina/$file/log/$var
			else
				rm /gochina/$file/log/$var
			fi
} &
done
