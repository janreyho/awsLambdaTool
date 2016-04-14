var=` TZ='Asia/Shanghai' date +%Y%m%d%H%M%S `
userfolder=~
echo $var

for file in ` ls ~/gochina/gochina/cpconfig `
do
{
	/bin/rm ~/gochina/$file/log/resolution.txt 
	/bin/rm ~/gochina/$file/log/transcode.txt
	
	ps -fe | grep "$userfolder/gochina/gochina/gochinajob.sh $1 $file" | grep -v grep
	if [ $? -ne 0 ]; then
		if [ "no" = $1 ];then
			~/gochina/gochina/gochinajob.sh $1 $file $var >> ~/gochina/$file/log/$var 2>&1
			cat ~/gochina/$file/log/resolution.txt >> ~/gochina/$file/log/$var
			cat ~/gochina/$file/log/transcode.txt >> ~/gochina/$file/log/$var
			/usr/bin/mail -s $file'-'$var'更新' janreyho@gmail.com < ~/gochina/$file/log/$var
		else
			~/gochina/gochina/gochinajob.sh $1 $file $var
		fi
	else
		echo "$userfolder/gochina/gochina/gochinajob.sh $1 $file exist" >> ~/gochina/$file/log/$var
	fi
} &
done
