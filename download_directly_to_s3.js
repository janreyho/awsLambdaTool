/*
npm install
export AWS_ACCESS_KEY_ID=<key>
export AWS_SECRET_ACCESS_KEY=<secret>
node download_directly_to_s3.js
*/
var streamingS3 = require('streaming-s3');
var request = require('request');
var Consumer = require('sqs-consumer');
var argv = require('minimist')(process.argv.slice(2));

function upload(url, out) {
  var bucket = 'ottcloud-video'

  var rStream = request.get(url);
  var uploader = new streamingS3(rStream, {accessKeyId: process.env.AWS_ACCESS_KEY_ID, secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY},
    {
      Bucket: bucket,
      Key: out
      //ContentType: 'text/html'
    },
    {
      concurrentParts: 2,
      waitTime: 10000,
      retries: 1,
      maxPartSize: 10*1024*1024,
    }
  );

  uploader.on('data', function (bytesRead) {
    console.log(bytesRead, ' bytes read.');
  });

  uploader.on('part', function (number) {
    console.log('Part ', number, ' uploaded.');
  });

  // All parts uploaded, but upload not yet acknowledged.
  uploader.on('uploaded', function (stats) {
    console.log('Upload stats: ', stats);
  });

  uploader.on('finished', function (resp, stats) {
    console.log('Upload finished: ', resp);
  });

  uploader.on('error', function (e) {
    console.log('Upload error: ', e);
  });

  uploader.begin(); // important if callback not provided.
}

function run_queue_server() {
  var self = this;
  var env = process.env.NODE_ENV || "development";
  var app = Consumer.create({
    queueUrl: 'https://sqs.us-east-1.amazonaws.com/629005883304/download_' + env,
    handleMessage: function (message, done) {
      // do some work with `message`
      //console.log(message.Body);
      try {
        var task = JSON.parse(message.Body);
        console.log(task);
        upload(task['url'], task['out']);

      } catch (e) {
        console.log(e);
      }
      done();
    }
  });

  app.on('error', function (err) {
    console.log(err.message);
  });

  app.start();
}

if (require.main === module) {
  if (argv._.length >= 1 && argv._[0] == 'queue') {
    //Shoryuken::Client.queues('download_development').send_message({url: "http://v3.cztv.com/cztv/vod/2016/04/18/A9A647BB7C464761A0C759EF8E826E50/h264_1500k_mp4.mp4", out: "zgl/test.mp4"}.to_json)
    run_queue_server();
  } else {
    console.log("running example");
    var url = "http://v3.cztv.com/cztv/vod/2016/04/18/A9A647BB7C464761A0C759EF8E826E50/h264_1500k_mp4.mp4";
    var out = "zgl/test.mp4";
    upload(url, out);
  }
}
