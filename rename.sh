#!/bin/bash
#. /home/ubuntu/tuxiaobei/txbtool/mapNameArray.sh
source ~/gochina/gochina/cpconfig/$2

echo "First Method: ${txbmapsrc[*]}"
echo "Second Method: ${txbmapdst[@]}"

function fun(){
        cp $txbtool"/"txbvar.json $txbtool"/"$2.json

        jq --arg cpvar $2 '.cp=$cpvar' $txbtool"/"$2.json > $txbtool"/"var1.json
        mv $txbtool"/"var1.json $txbtool"/"$2.json
        # 日期目录
        for file1 in ` ls $1 `
        do
        if [ -d $1"/"$file1 ]; then
                echo $file1
                pos1=0
                # 专辑目录
                for file2 in ` ls $1"/"$file1 `
                do


                        if [ -d $1"/"$file1"/"$file2 ]; then

                        # cd $1
                        # cd ..
                        pos2=0
                        # 节目名称
                        for file3 in ` ls $1"/"$file1"/"$file2 `
                        do
                        echo $file3
                          namevar=`echo $file3 | sed 's/\([0-9]*\)\(.*\)\(\..*\)/\2/g'`
                          idvar=`echo $file3 | sed 's/\([0-9]*\)\(.*\)\(\..*\)/\1/g'`
                          jq --arg var $namevar --arg num1 $pos1 --arg num2 $pos2 '.albums[$num1 | tonumber].videos[$num2 | tonumber].name=$var' $txbtool"/"$2.json > $txbtool"/"var1.json
                          mv $txbtool"/"var1.json $txbtool"/"$2.json
                          jq --arg var $idvar --arg num1 $pos1 --arg num2 $pos2 '.albums[$num1 | tonumber].videos[$num2 | tonumber].id=$var' $txbtool"/"$2.json > $txbtool"/"var1.json
                          mv $txbtool"/"var1.json $txbtool"/"$2.json

                          pos2=`expr $pos2 + 1`

                        done

                        cd $1"/"$file1"/"$file2
                        # rename 's/^(\d+)(?:[^.]*)(\.\w+)/$1$2/' *
                        #cd -


                        for ((i=0; i<${#txbmapsrc[@]}; i++))
                        do
                                #echo $i
                                echo $file2 | grep -q "${txbmapsrc[i]}"
                                if [ $? -eq 0 ]; then
                                        echo $file2"->"${txbmapdst[i]}
                                        jq --arg namevar ${txbmapsrc[i]} --arg num1 $pos1 '.albums[$num1 | tonumber].name=$namevar' $txbtool"/"$2.json > $txbtool"/"var1.json
                                        mv $txbtool"/"var1.json $txbtool"/"$2.json
                                        jq --arg idvar ${txbmapdst[i]} --arg num1 $pos1 '.albums[$num1 | tonumber].id=$idvar' $txbtool"/"$2.json > $txbtool"/"var1.json
                                        mv $txbtool"/"var1.json $txbtool"/"$2.json
                                        mv $1"/"$file1"/"$file2 $1"/"$file1"/"${txbmapdst[i]}
                                fi
                        done

                        fi
                pos1=`expr $pos1 + 1`

                done
        fi
        done
        cat $txbtool"/"$2.json
}

fun $1 $2
