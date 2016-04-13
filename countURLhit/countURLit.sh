#!/bin/bash

# ./countURLHit.sh http://xxx.com url.txt

url="null"
linenum=0
urlnum=0
cacheNum=0
hitnum=0
echo "" > awkalldata.txt
while true
do
  linenum=`expr $linenum + 1`
  echo $linenum
  echo $linenum >> awkalldata.txt
  url=`sed -n $linenum"p" $2`
  if [[ "" == $url ]];then
  	break
  fi
  # `(( $linenum++ ))`

  if [[ "null" != $url ]];then
  	urlnum=`expr $urlnum + 1`
  	echo $1$url
  	echo $1$url >> awkalldata.txt
  	curl -I $1$url > /tmp/awkdata.txt
  	cat /tmp/awkdata.txt >> awkalldata.txt
  	hitstr=`awk 'BEGIN{FS=": "} /X-Cache/{print $2}' /tmp/awkdata.txt`
  	echo $hitstr
  	if [[ "" != $hitstr ]];then
  		cacheNum=`expr $cacheNum + 1`
  	fi
  	# if [[ "HIT" == $hitstr ]];then
  	if [[ $hitstr =~ "HIT" ]]; then
  		hitnum=`expr $hitnum + 1`
  	fi
  fi
done

echo "linenum:"$linenum
echo "urlnum:"$urlnum
echo "cacheNum:"$cacheNum
echo "hitnum:"$hitnum