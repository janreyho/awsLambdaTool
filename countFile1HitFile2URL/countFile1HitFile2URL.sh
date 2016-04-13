#!/bin/bash

# ./countFile1HitFile2URL.sh Partial.txt full.txt 

url=""
linenum=0

while true
do
  linenum=`expr $linenum + 1`
  echo $linenum
  url=`sed -n $linenum"p" $2`
  echo $url
  if [[ "" == $url ]];then
  	break
  fi

  grep -n $url $1
  if [[ $? != 0 ]]; then
    echo $url >> notINpartial.txt
  fi

done
