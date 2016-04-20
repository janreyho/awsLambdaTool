#!/bin/bash

#./download.sh http://xxx.com urltest /path
#sudo ./downloadurl.sh http://img1.gochinatv.com urltest /mnt/s3/zhongguolan/videos/src
#./downloadurl.sh http://vod.vegocdn.com chinablueURL1 /mnt/s3/zhongguolan/videos/src > download_zgl.log 2>&1 &

url="null"
linenum=0
urlnum=0
while true
do
  linenum=`expr $linenum + 1`
  echo $linenum
  url=`sed -n $linenum"p" $2`
  if [[ "" == $url ]];then
  	break
  fi
  # `(( $linenum++ ))`

  if [[ "null" != $url ]];then
  	urlnum=`expr $urlnum + 1`
  	echo $1$url
    httpNum=`curl -I -m 10 -o /dev/null -s -w %{http_code} $1$url`
    echo $httpNum
    if [[ 200 != $httpNum ]]; then
      echo $httpNum':'$url >> errorurl.txt
    else
      curl --create-dirs -o $3$url $1$url
      if [[ 0 != $? ]]; then
        echo $? >> errorurl.txt
        echo $url >> errorurl.txt
      fi
    fi


  fi
done

echo "linenum:"$linenum
echo "urlnum:"$urlnum
