#!/bin/bash

VPATH="/gochina/dongfangjiahe"

function log_to_file() {
	echo `date +"%Y-%m-%d %H:%M:%S"` $1 >> log/`date +%Y%m%d`.log
}

function lftp_up() {
dstpath=nwx`date +%Y%m%d%H%M%S`
log_to_file "mkdir -p $dstpath"
log_to_file "put -c -O $dstpath $2"
log_to_file "put -c -O $dstpath $3"
log_to_file "put -c -O $dstpath $1delivery.complete"
lftp -u gonggongkongjian, sftp://sftp.ottcloud.tv <<EOF
	mkdir -p $dstpath
	put -c -O $dstpath $2
	put -c -O $dstpath $3
	put -c -O $dstpath $1delivery.complete
	quit
EOF
	return 0
}

/usr/local/bin/inotifywait -mrq --timefmt '%d/%m/%y/%H:%M' --format '%T %w %f' -e close_write,moved_to $VPATH |
	while read TIME DIR FILENAME
	do
		if [[ $FILENAME = "delivery.complete" ]]; then
			log_to_file "[$DIR] task transfter complete"
			DSTDIR="${DIR#/*/}"
			VFILE=`ls $DIR*.mp4`
			#CFILE=`ls $DIR*.csv`
			CFILE=`ls $DIR*.csv 2> /dev/null || ls $DIR*.xml 2> /dev/null`
			log_to_file "DIR=$DIR"
			log_to_file "DSTDIR=$DSTDIR"
			log_to_file "VFILE=$VFILE"
			log_to_file "CFILE=$CFILE"
			{
				lftp_up $DIR $VFILE $CFILE && log_to_file "Task [$DIR] sync to sftp server OK."
			} &
		else
			log_to_file "[$DIR$FILENAME] transfter complete"
		fi
	done
