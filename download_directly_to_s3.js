/*
npm install request
npm install streaming-s3
export AWS_ACCESS_KEY_ID=<key>
export AWS_SECRET_ACCESS_KEY=<secret>
node download_directly_to_s3.js
*/
var streamingS3 = require('streaming-s3'),
    request = require('request');

var url = "http://v3.cztv.com/cztv/vod/2016/04/18/A9A647BB7C464761A0C759EF8E826E50/h264_1500k_mp4.mp4";
var out = "zgl/test.mp4";
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

uploader.begin(); // important if callback not provided.

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

