#!/bin/bash
source ~/gochina/gochina/cpconfig/$2
echo ""
echo ""
echo "#############"$2
echo ` TZ='Asia/Shanghai' date +%Y-%m-%d-%H-%M-%S `": tuxiaobei job start"
echo $localdir
echo $bakdir
echo $s3dir
echo $s3bucket
echo $bucksrc
echo $buckdst


echo "bypy syndown /$2 $localdir"
if [ "$txbdown" == "true" ]; then
	/usr/local/bin/bypy -r 1000000 syncdown /$2 $localdir
fi

num=`ls $localdir | wc -l`
echo $num
if [ 0 == $num ]; then
	exit 0
fi


treelogfile=tree_`TZ='Asia/Shanghai' date +%Y-%m-%d`.log
tree $localdir > $logpath"/"treelogfile
echo "rename.sh $localdir"
if [ "$txbrename" == "true" ]; then
	$txbtool"/"rename.sh $localdir $2
fi
tree $localdir >> $logpath"/"treelogfile
/usr/bin/mail -s $2'-'$var'更新tree' hejiayi@gochinatv.com,zhixueyong@gochinatv.com,caolei@gochinatv.com < $logpath"/"treelogfile
/usr/bin/mail -s $2'-'$var'更新json' hejiayi@gochinatv.com,zhixueyong@gochinatv.com,caolei@gochinatv.com < $txbtool/$2.json


echo "cp -rf $localdir"/"* $s3dir"
if [ "$txbcptos3" == "true" ]; then
	cp -rf $localdir"/"* $s3dir
fi


for file in ` ls $localdir `
do
	echo "python awsTranscodeHls.py -b $s3bucket -i $bucksrc"/"$file -o $buckdst -t $1"
	if [ "$txbtrancode" == "true" ]; then
		python $txbtool"/"awsTranscodeHls.py -f folder -b $s3bucket -i $bucksrc"/"$file -o $buckdst -t $1
	fi

	echo "bypy rm $file"
	if [ "$txbremoterm" == "true" ]; then
		/usr/local/bin/bypy rm $2"/"$file
	fi
done

echo "rmdd $localdir"/"*"
if [ "$txblocalmv" == "true" ]; then
	rm -rf $localdir"/"*
fi



echo ` TZ='Asia/Shanghai' date +%Y-%m-%d-%H-%M-%S `": tuxiaobei job done"
