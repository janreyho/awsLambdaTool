var=` TZ='Asia/Shanghai' date +%Y-%m-%d `
userfolder=~
echo $var

for file in ` ls ~/gochina/gochina/cpconfig `
do
{
	ps -fe | grep "$userfolder/gochina/gochina/gochinajob.sh $1 $file" | grep -v grep
	if [ $? -ne 0 ]; then
	~/gochina/gochina/gochinajob.sh $1 $file >> ~/gochina/$file/log/$var 2>&1
	/usr/bin/mail -s $file'-'$var'更新' janreyho@gmail.com < ~/gochina/$file/log/$var
	else
		echo "$userfolder/gochina/gochina/gochinajob.sh $1 $file exist" >> ~/gochina/$file/log/$var
	fi
} &
done
