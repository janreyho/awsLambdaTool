# aws－lambda 转码服务

## 前提条件
* Python 2.7 (At the time of writing this, AWS Lambda only supports Python 2.7).
* Pip (~8.1.1)
* Virtualenv (~15.0.0)
* Virtualenvwrapper (~4.7.1)

## 请求数据格式

	{
	  "bucket": "ottcloud",
	  "contentprovider": "publicspace",
	  "dst": "publicspace/videos/dst/test/",          //必须以/结尾
	  "src": "publicspace/videos/src/2016.04.20/",    //如果是目录以/结尾，如果是文件，必须是mp4
	  "testflag": "test",				//no:正式转码，其他:测试
	  "time": "20160426000001",
	  "type": "mp4",					//生成文件类型mp4或m3u8
	  "v_bitrate": 2700000,			//源文件码率，单位bps
	  "v_height": 720				//源文件分辨率，480，720，或1080
	}
说明：src和dst必须是bucket中的目录，且必须是同一个bucket

## 示例 发送转码请求
x-api-key字段需要更换为access key

	curl --header "Content-Type:application/json" \
		 --header "x-api-key: xxxxxxxxxxxxxxxxxxxxxxx" \
	     --request POST \
	     --data '{"bucket":"ottcloud","contentprovider":"publicspace","dst":"publicspace/videos/dst/test/","src":"publicspace/videos/src/2016.04.20/","testflag":"test","time":"20160426000001","type":"mp4","v_bitrate":2700000,"v_height":720}' \
	     https://wbxy19lbn5.execute-api.ap-northeast-1.amazonaws.com/prod/videoTranscode

## 返回数据格式

	{
	  "videos": [
	    {
	      "dst": "publicspace/videos/dst/clips/2015_20160426000001/2015.m3u8",
	      "error": "no",
	      "keyoutpath": "publicspace/videos/dst/clips/",
	      "output_key": "2015",
	      "src": "publicspace/videos/src/2016.04.20/clips/2015.mp4",
	      "status": "transcode"
	    },
	    {
	      "dst": "publicspace/videos/dst/cp/1_20160426000001/1.m3u8",
	      "error": "exist",
	      "keyoutpath": "publicspace/videos/dst/cp/",
	      "output_key": "1",
	      "src": "publicspace/videos/src/2016.04.20/cp/1.mp4",
	      "status": "exist"
	    },
	    {
	      "error": "not .mp4"
	    }
	  ]
	}
说明：该返回数据表明：请求三个文件转码,第一个文件2015.mp4成功完成，第二个文件1.mp4之前已经转过，第三个文件发生错误（原文件不是.mp4）

## 开发方法
仅使用转码服务，下面内容无需看
Python-lambda is a toolset for developing and deploying serverless Python code in AWS Lambda.

Begin by creating a new virtualenv and project folder.

	$ mkvirtualenv pylambda
	(pylambda) $ mkdir folder
	(pylambda) $ cd folder
	(pylambda) $ pip install python-lambda
	(pylambda) $ lambda init
This will create the following files: event.json, __init__.py, service.py, and config.yaml.

	(pylambda) $ lambda invoke -v		//本地测试
	(pylambda) $ lambda deploy			//部署到awsLambda


## 备注

[python-lambda](https://github.com/nficano/python-lambda)

[使用virtualenv搭建独立的Python环境](http://qicheng0211.blog.51cto.com/3958621/1561685)
