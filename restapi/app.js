var express = require('express');
var child_process = require('child_process');
var app = express();

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
        next();
    }
});

var usage = '\
<html>\
  <table border="1">\
    <tr><td>classify   </td><td>  [Caffe] </td><td><a href="http://localhost:8080/api/v1/classify/bvlc_reference_caffenet%2Fdata%2Fsample%2Fad_sunglass.png,3">http://localhost:8080/api/v1/classify/bvlc_reference_caffenet%2Fdata%2Fsample%2Fad_sunglass.png,3</a></td></tr>\
    <tr><td>count_line </td><td>  [Spark] </td><td>http://localhost:8080/api/v1/classify </td></tr>\
    <tr><td>du         </td><td>  [HDFS]  </td><td>http://localhost:8080/api/v1/classify </td></tr>\
    <tr><td>head       </td><td>  [Spark] </td><td>http://localhost:8080/api/v1/classify </td></tr>\
    <tr><td>ls         </td><td>  [HDFS]  </td><td>http://localhost:8080/api/v1/classify </td></tr>\
    <tr><td>ngram_ko   </td><td>  [Spark] </td><td>http://localhost:8080/api/v1/classify </td></tr>\
    <tr><td>sql        </td><td>  [Hive]  </td><td>http://localhost:8080/api/v1/classify </td></tr>\
    <tr><td>sql2       </td><td>  [Spark] </td><td>http://localhost:8080/api/v1/classify </td></tr>\
    <tr><td>text       </td><td>  [HDFS]  </td><td>http://localhost:8080/api/v1/classify </td></tr>\
    <tr><td>tf_ko      </td><td>  [Spark] </td><td>http://localhost:8080/api/v1/classify </td></tr>\
    <tr><td>train_mnist</td><td>  [Caffe] </td><td>http://localhost:8080/api/v1/classify </td></tr>\
    <tr><td>word_cloud </td><td>  [R]     </td><td>http://localhost:8080/api/v1/classify </td></tr>\
  </table>\
</html>';

app.get('/api/v1/:op/:param', function(req, res) {
    console.log(req.params.op);
    console.log(typeof(req.params.op));
    console.log(req.params.param);
    console.log(typeof(req.params.param));
    console.log(req.params.op + ':' + req.params.param);
    console.log(['-f', '/Users/dongjoon/tip/cli/fabfile.py', req.params.op + ":" + req.params.param]);

    child = child_process.exec('/usr/local/bin/fab -f /Users/dongjoon/tip/cli/fabfile.py ' + req.params.op + ':' + req.params.param,
        function (error, stdout, stderr) {
            console.log('stdout: ' + stdout);
            console.log('stderr: ' + stderr);
            res.send(stdout.toString());
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
