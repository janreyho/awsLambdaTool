#全景中国自动化运营工具

### 定时任务

	//北京时间24:00:00，任务开始执行
	crontab －e
	0 16 * * * ~/gochina/gochina/startjob.sh no

### 目录cpconfig中，一个配置文件对应一个CP

任务开启后，可以根据不同的配置文件，对不同CP的原片，进行下载，修改目录和文件名，上传s3，进行转码。


### 对不同码率分辨率的mp4库，智能生成多码率m3u8
	python awsTranscodeHls.py -u 20160413000001 -b ottcloud -c zhongguolan -f folder -i zhongguolan/videos/src -o zhongguolan/videos/dst -t no > work.log &
