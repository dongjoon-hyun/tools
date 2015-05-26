var express = require('express');
var os = require('os');
var child_process = require('child_process');
var app = express();
var user = 'nobody';

app.use(function(req, res, next) {
    var auth;

    if (req.headers.authorization) {
      auth = new Buffer(req.headers.authorization.substring(6), 'base64').toString().split(':');
    }

    if (!auth || auth[0] !== 'hadoop' || auth[1] !== 'tip') {
        res.statusCode = 401;
        res.setHeader('WWW-Authenticate', 'Basic realm="T Intelligence Platform"');
        res.end('Unauthorized');
    } else {
        user = auth[0];
        next();
    }
});

var usage = '\
<html>\
  <table border="1">\
    <tr><td>classify   </td><td>  [Caffe] </td><td><a href="placeholder/classify/bvlc_reference_caffenet%2Fdata%2Fsample%2Fad_sunglass.png,3">placeholder/classify/bvlc_reference_caffenet%2Fdata%2Fsample%2Fad_sunglass.png,3</a></td></tr>\
    <tr><td>count      </td><td>  [HDFS]  </td><td><a href="placeholder/count/%2Fdata%2Ftext%2Fnewsgroup">placeholder/count/%2Fdata%2Ftext%2Fnewsgroup</a></td></tr>\
    <tr><td>count_line </td><td>  [Spark] </td><td><a href="placeholder/count_line/%2Fdata%2Fimage%2Fimagenet%2F%2A.txt">placeholder/count_line/%2Fdata%2Fimage%2Fimagenet%2F%2A.txt</a></td></tr>\
    <tr><td>du         </td><td>  [HDFS]  </td><td><a href="placeholder/du/%2Fdata%2Fsample">placeholder/du/%2Fdata%2Fsample</a></td></tr>\
    <tr><td>head       </td><td>  [Spark] </td><td><a href="placeholder/head/%2Fdata%2Fimage%2Fimagenet%2F%2A.txt,5">placeholder/head/%2Fdata%2Fimage%2Fimagenet%2F%2A.txt,5</a></td></tr>\
    <tr><td>ls         </td><td>  [HDFS]  </td><td><a href="placeholder/ls/%2Fdata%2Fsample">placeholder/ls/%2Fdata%2Fsample</a></td></tr>\
    <tr><td>ngram_ko   </td><td>  [Spark] </td><td><a href="placeholder/ngram_ko/2,%2Fuser%2Fhadoop%2Ftf_result,%2Fuser%2Fhadoop%2Fngram_result">placeholder/ngram_ko/2,%2Fuser%2Fhadoop%2Ftf_result,%2Fuser%2Fhadoop%2Fngram_result</a></td></tr>\
    <tr><td>sql        </td><td>  [Hive]  </td><td><a href="placeholder/sql/%27select%20count(%2A)%20from%20data.news%27">placeholder/sql/%27select%20count(%2A)%20from%20data.news%27</a></td></tr>\
    <tr><td>sql2       </td><td>  [Hive]  </td><td><a href="placeholder/sql2/%27select%20count(%2A)%20from%20data.news%27">placeholder/sql2/%27select%20count(%2A)%20from%20data.news%27</a></td></tr>\
    <tr><td>text       </td><td>  [HDFS]  </td><td><a href="placeholder/text/%2Fdata%2Fsample%2Fhani_news.head.txt.gz,5">placeholder/text/%2Fdata%2Fsample%2Fhani_news.head.txt.gz,5</a></td></tr>\
    <tr><td>tf_ko      </td><td>  [Spark] </td><td><a href="placeholder/tf_ko/%2Fdata%2Ftext%2Fnews%2Fhani%2F%2A,%2Fuser%2Fhadoop%2Ftf_result">placeholder/tf_ko/%2Fdata%2Ftext%2Fnews%2Fhani%2F%2A,%2Fuser%2Fhadoop%2Ftf_result</a></td></tr>\
    <tr><td>train_mnist</td><td>  [Caffe] </td><td><a href="placeholder/train_mnist/gpu=0,mode=GPU,net=net.prototxt">placeholder/train_mnist/gpu=0,mode=GPU,net=net.prototxt</a></td></tr>\
    <tr><td>word_cloud </td><td>  [R]     </td><td><a href="placeholder/word_cloud/%2Fuser%2Fhadoop%2Fnews_word_count.txt">placeholder/word_cloud/%2Fuser%2Fhadoop%2Fnews_word_count.txt</a></td></tr>\
  </table>\
</html>';
var hostname = os.hostname();
usage = usage.replace(/placeholder/g, 'http://' + hostname + ':8080/api/v1');

app.get('/api/v1/:op/:param', function(req, res) {
    console.log(user + "@" + req.ip + ": " + req.originalUrl);
    console.log('/usr/local/bin/fab -f ../cli/fabfile.py ' + req.params.op + ':' + req.params.param);

    child = child_process.exec('/usr/local/bin/fab -f ../cli/fabfile.py ' + req.params.op + ':' + req.params.param,
        function (error, stdout, stderr) {
            console.log('stdout: ' + stdout);
            console.log('stderr: ' + stderr);
            res.setHeader('Access-Control-Allow-Origin', '*');
            res.json({ 
                "user": user,
                "ip": req.ip,
                "request": req.originalUrl,
                "result": stdout.toString() 
            });
            if (error !== null) {
                console.log('exec error: ' + error);
            }
        });
});

app.get('/api/v1/:op', function(req, res) {
  res.send(usage);
});

app.get('/api/v1/', function(req, res) {
  res.send(usage);
});

app.listen(process.env.PORT || 8080);
