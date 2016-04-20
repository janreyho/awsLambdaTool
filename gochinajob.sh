#!/bin/bash
source ~/gochina/gochina/cpconfig/$2
echo ""
echo ""
echo "#############"$2
echo $3 ": tuxiaobei job start"
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
	$txbtool"/"rename.sh $localdir $2 $3 $1
fi
tree $localdir >> $logpath"/"treelogfile

cat $txbtool/$2.json >> $logpath"/"treelogfile
if [ "no" = $1 ];then
	echo sendemail2
	/usr/bin/mail -s $2'_'$3'更新tree' hejiayi@gochinatv.com,zhixueyong@gochinatv.com,caolei@gochinatv.com < $logpath"/"treelogfile
	curl -F stream=@$txbtool/$2.json 'http://vrsclone.herokuapp.com/api/v1/episodes/incoming.json'
	mv $txbtool/$2.json $txbtool/data/$2"_"$3.json
else
	/usr/bin/mail -s $2'_'$3'更新tree' hejiayi@gochinatv.com < $logpath"/"treelogfile
fi

echo "cp -rf $localdir"/"* $s3dir"
if [ "$txbcptos3" == "true" ]; then
	cp -rf $localdir"/"* $s3dir
fi


for file in ` ls $localdir `
do
	echo "python awsTranscodeHls.py -u $3 -f folder -b $s3bucket -c $2 -i $bucksrc"/"$file -o $buckdst -t $1"
	if [ "$txbtrancode" == "true" ]; then
		python $txbtool"/"awsTranscodeHls.py -u $3 -f folder -b $s3bucket -c $2 -i $bucksrc"/"$file -o $buckdst -t $1
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
