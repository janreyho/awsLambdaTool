var=` TZ='Asia/Shanghai' date +%Y-%m-%d `
echo $var

for file in ` ls ~/gochina/gochina/cpconfig `
do
	#~/gochina/gochina/gochinajob.sh no >> ~/gochina/$file/log/$var 2>&1
	~/gochina/gochina/gochinajob.sh $1 $file >> ~/gochina/$file/log/$var 2>&1
	/usr/bin/mail -s $file'-'$var'更新' janreyho@gmail.com < ~/gochina/$file/log/$var
done

