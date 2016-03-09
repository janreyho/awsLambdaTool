#!/bin/bash

#txbdown=true txbrename=true txbcptos3=true txbtrancode=true txbremoterm=true txblocalmv=true ./txbjob.sh test
localdir=/home/ubuntu/tuxiaobei/src
bakdir=/home/ubuntu/tuxiaobei/srcbak
s3dir=/mnt/s3/tuxiaobei/videos/src
s3bucket=ottcloud
bucksrc=tuxiaobei/videos/src
buckdst=tuxiaobei/videos/dst
txbtool=/home/ubuntu/tuxiaobei/txbtool
logpath=/home/ubuntu/tuxiaobei/log

echo ""
echo ""
echo "#############"
echo ` TZ='Asia/Shanghai' date +%Y-%m-%d-%H-%M-%S `": tuxiaobei job start"
echo $localdir
echo $bakdir
echo $s3dir
echo $s3bucket
echo $bucksrc
echo $buckdst


echo "bypy syndown / $localdir"
if [ "$txbdown" == "true" ]; then
	/usr/local/bin/bypy -r 1000000 syncdown / $localdir
fi

num=`ls $localdir | wc -l`
echo $num
if [ 0 == $num ]; then
	exit 0
fi


treelogfile=tree_`TZ='Asia/Shanghai' date +%Y-%m-%d`.log
tree $localdir >> $logpath"/"treelogfile
echo "renametxb.sh $localdir"
if [ "$txbrename" == "true" ]; then
	$txbtool"/"renametxb.sh $localdir
fi
tree $localdir >> $logpath"/"treelogfile
/usr/bin/mail -s 'tuxiaobei-'$var'更新' hejiayi@gochinatv.com,zhixueyong@gochinatv.com,caolei@gochinatv.com,liruizheng@gochinatv.com < $logpath"/"treelogfile



echo "cp -rf $localdir"/"* $s3dir"
if [ "$txbcptos3" == "true" ]; then
	cp -rf $localdir"/"* $s3dir
fi


for file in ` ls $localdir `
do
	echo "python awsTranscodeHls.py -b $s3bucket -i $bucksrc"/"$file -o $buckdst -t $1"
	if [ "$txbtrancode" == "true" ]; then
		python $txbtool"/"awsTranscodeHls.py -b $s3bucket -i $bucksrc"/"$file -o $buckdst -t $1
	fi

	echo "bypy rm $file"
	if [ "$txbremoterm" == "true" ]; then
		/usr/local/bin/bypy rm $file
	fi
done

echo "mv $localdir"/"* $bakdir"
if [ "$txblocalmv" == "true" ]; then
	mv $localdir"/"* $bakdir
fi



echo ` TZ='Asia/Shanghai' date +%Y-%m-%d-%H-%M-%S `": tuxiaobei job done"
