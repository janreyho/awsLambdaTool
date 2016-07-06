#!/bin/bash
source /gochina/gochina/cpconfig/$2
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


echo "bypy syncdown /$2 $localdir"
if [ "$txbdown" == "true" ]; then
	/usr/local/bin/bypy -r 1000000 syncdown /$2 $localdir
fi

num=`ls $localdir | wc -l`
echo $num
if [ 0 == $num ]; then
	exit 0
fi


treelogfile=tree_`TZ='Asia/Shanghai' date +%Y-%m-%d`.log
tree -h $localdir > $logpath"/"treelogfile
echo "rename.sh $localdir"
if [ "$txbrename" == "true" ]; then
	$txbtool"/"rename.sh $localdir $2 $3 $1
fi
tree $localdir >> $logpath"/"treelogfile

cat $txbtool/$2.json >> $logpath"/"treelogfile
echo "$txbtool"/"sendmail.py -s $2'_'$3'newtree' -f $logpath"/"treelogfile"
python $txbtool"/"sendmail.py -s $2'_'$3'newtree' -f $logpath"/"treelogfile
if [ "no" = $1 ];then
	if [ "tuxiaobei" = $2 ];then
		curl -F stream=@$txbtool/$2.json 'http://vrsclone.herokuapp.com/api/v1/episodes/incoming.json'
	fi
	mv $txbtool/$2.json $datapath/$2"_"$3.json
fi

echo "cp -rf $localdir"/"* $s3dir"
if [ "$txbcptos3" == "true" ]; then
	cp -rf $localdir"/"* $s3dir
fi


for file in ` ls $localdir `
do
	echo "python awsTranscode.py -u $3 -f folder -b $s3bucket -c $2 -s $bucksrc"/"$file -d $buckdst -t $1"
	if [ "$txbtrancode" == "true" ]; then
		python $txbtool"/"awsTranscode.py -u $3 -f folder -b $s3bucket -c $2 -s $bucksrc"/"$file -d $buckdst -t $1
		cat /gochina/$2/log/resolution_$3.txt
		cat /gochina/$2/log/transcode_$3.txt
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
