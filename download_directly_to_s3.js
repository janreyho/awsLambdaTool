/*
npm install
export AWS_ACCESS_KEY_ID=<key>
export AWS_SECRET_ACCESS_KEY=<secret>
export PUSHER_APP_ID=<app_id>
export PUSHER_KEY=<key>
export PUSHER_SECRET=<secret>
node download_directly_to_s3.js
*/
var streamingS3 = require('streaming-s3');
var request = require('request');
var Consumer = require('sqs-consumer');
var argv = require('minimist')(process.argv.slice(2));
var http = require('http');
var querystring = require('querystring');
var uploadedBytes = 0;
var Pusher = require('pusher');
// var airbrake = require('airbrake').createClient("117109", "3d3cc8749439b5878038d22d079ce0bf");

var pusher = new Pusher({
  appId: process.env.PUSHER_APP_ID, //'220674',
  key: process.env.PUSHER_KEY, //'65a7daa2d92d664e54ec',
  secret: process.env.PUSHER_SECRET, //'7435d50f2981e18de1d5',
  encrypted: true
});

function upload(url, out, size, eid) {
  var bucket = 'ottcloud';

  var rStream = request.get(url);
  var uploader = new streamingS3(rStream, {accessKeyId: process.env.AWS_ACCESS_KEY_ID, secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY},
    {
      Bucket: bucket,
      Key: out
      //ContentType: 'text/html'
    },
    {
      concurrentParts: 3,
      waitTime: 20000,
      retries: 1,
      maxPartSize: 5000*1024*1024,
    }
  );

  uploader.on('data', function (bytesRead) {
    uploadedBytes = uploadedBytes + bytesRead
    console.log(bytesRead, ' bytes read.');
    console.log("uploadedBytes:", uploadedBytes);
    console.log("Uploading Rate:", uploadedBytes/size);
    if(size > 0) {
      if(uploadedBytes/size < 1 && uploadedBytes/size*100%10 < 0.3) {
        notify_download_progress(eid, uploadedBytes/size);
        pusher.trigger('vego_channel', 'get_download_progress_'+eid, {'rate': uploadedBytes/size});
      }
    }
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
    console.log('State:', stats);
    uploadedBytes = 0;
    notify_to_boss(eid, stats);
    pusher.trigger('vego_channel', 'finish_'+eid, {'rate': 1});
  });

  uploader.on('error', function (e) {
    console.log('Upload error: ', e);
    notify_download_progress(eid, '-1');
    pusher.trigger('vego_channel', 'get_error_'+eid, {'message': e});
  });

  uploader.begin(); // important if callback not provided.
}

function notify_to_boss(eid, stats){
  var post_data = querystring.stringify({'eid' : eid, 'state' : stats });
  var req = http.request({
    // host: 'vrsclone.herokuapp.com',
    host: 'mgtv.admin.vrsclone.dev',
    path: '/api/v1/episodes/transfer.json',
    method: 'POST',
    headers: {
      'X-REQUESTER': 'BOSS-DOWNLOAD',
      'Content-Type': 'application/x-www-form-urlencoded',
      'Content-Length': Buffer.byteLength(post_data)
    }
  }, function(res) {
    res.setEncoding('utf8');
  });
  req.write(post_data);
  req.end();
}

function notify_download_progress(eid, rate){
  var post_data = querystring.stringify({'eid' : eid, 'rate' : rate });
  var req = http.request({
    // host: 'vrsclone.herokuapp.com',
    host: 'mgtv.admin.vrsclone.dev',
    path: '/api/v1/episodes/download_progress.json',
    method: 'POST',
    headers: {
      'X-REQUESTER': 'BOSS-DOWNLOAD',
      'Content-Type': 'application/x-www-form-urlencoded',
      'Content-Length': Buffer.byteLength(post_data)
    }
  }, function(res) {
    res.setEncoding('utf8');
  });
  req.write(post_data);
  req.end();
}

function run_queue_server() {
  var self = this;
  var env = process.env.NODE_ENV || "development";
  var app = Consumer.create({
    queueUrl: 'https://sqs.us-east-1.amazonaws.com/629005883304/download_' + env,
    handleMessage: function (message, done) {
      // do some work with `message`
      console.log(message.Body);
      try {
        var task = JSON.parse(message.Body);
        console.log(task);
        upload(task['url'], task['out'], task['size'], task['eid']);

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
    var url = "https://s3.amazonaws.com/ottcloud-video/zgl/rm.zip";
    var out = "zgl/rm-1.zip";
    var size = 1232242342;
    var eid = 8332
    try {
      upload(url, out, size, eid);
    } catch (e) {
      console.log(e);
      // airbrake.notify(e);
    }
  }
}
