#!/bin/bash
#. /home/ubuntu/tuxiaobei/txbtool/mapNameArray.sh
source ~/gochina/gochina/cpconfig/$2

echo "First Method: ${txbmapsrc[*]}"
echo "Second Method: ${txbmapdst[@]}"

function fun(){
        for file1 in ` ls $1 `
        do
        if [ -d $1"/"$file1 ]; then
                echo $file1
                for file2 in ` ls $1"/"$file1 `
                do
                        if [ -d $1"/"$file1"/"$file2 ]; then

                        cd $1"/"$file1"/"$file2 
                        rename 's/^(\d+)(?:[^.]*)(\.\w+)/$1$2/' *
                        #cd -
                        echo "hejiayi"

                        for ((i=0; i<${#txbmapsrc[@]}; i++))
                        do
                                #echo $i
                                echo $file2 | grep -q "${txbmapsrc[i]}"
                                if [ $? -eq 0 ]; then
                                        echo $file2"->"${txbmapdst[i]}
                                        mv $1"/"$file1"/"$file2 $1"/"$file1"/"${txbmapdst[i]}
                                fi
                        done
                        

                        fi
                done
        fi
        done
}

fun $1
