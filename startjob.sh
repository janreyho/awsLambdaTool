var=` TZ='Asia/Shanghai' date +%Y%m%d%H%M%S `
echo $var

for file in ` ls /gochina/gochina/cpconfig `
do
{
	source /gochina/gochina/cpconfig/$file
	ps -fe | grep "/gochina/gochina/gochinajob.sh $1 $file" | grep -v grep
	if [ $? -ne 0 ]; then
		# if [ "no" = $1 ];then
			/gochina/gochina/gochinajob.sh $1 $file $var >> /gochina/$file/log/$var 2>&1
			if [ -f /gochina/$file/log/resolution_$var ]; then
			/usr/bin/mail -s $file'-'$var'更新' $mailrecverstest < /gochina/$file/log/$var
			else
				rm /gochina/$file/log/$var
			fi
		# else
		# 	/gochina/gochina/gochinajob.sh $1 $file $var
		# fi
	else
		echo "/gochina/gochina/gochinajob.sh $1 $file exist" >> /gochina/$file/log/$var
	fi
} &
done
