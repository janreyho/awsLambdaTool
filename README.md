#全景中国自动化运营工具

### 定时任务

	//北京时间24:00:00，任务开始执行
	crontab －e
	0 16 * * * /home/ubuntu/tuxiaobei/txbtool/startjob.sh

###从百度云自动下载，整理目录和文件名，转码

	//定时执行如下命令即可完成，自动下载，目录及文件名整理，转码
	//txbdown:从百度云下载
	//txbrename:整理目录文件
	//txbcptos3：拷贝到s3
	//txbtrancode:转码
	//txbremoterm:删除从百度云已下载的目录
	//txblocalmv:移除本地下载的目录
	txbdown=true txbrename=true txbcptos3=true txbtrancode=true txbremoterm=true txblocalmv=true ./txbjob.sh no


### 多码率hls视频预热

	//下载前
	➜  txb  tree english
	english
	├── 1
	│   └── 1.m3u8
	└── 2
	    └── 2.m3u8

	//自动下载多码率m3u8及相关ts
	➜  txb  ./download-hls.sh english http://video.ottcloud.tv/tuxiaobei/videos/dst

	//下载后
	➜  txb  tree  english -L 2
	english
	├── 1
	│   ├── 1.m3u8
	│   ├── hls0400k
	│   ├── hls0800k
	│   ├── hls1600k
	│   ├── hls2500k
	│   └── hls4001k
	└── 2
	    ├── 2.m3u8
	    ├── hls0400k
	    ├── hls0800k
	    ├── hls1600k
	    ├── hls2500k
	    └── hls4001k
