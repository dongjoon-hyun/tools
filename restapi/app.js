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
    <tr><td>classify   </td><td>  [Caffe] </td><td>http://localhost:8080/api/v1/classify </td></tr>\
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

app.get('/api/v1/:op?:param', function(req, res) {
    child = child_process.spawn('/usr/local/bin/fab', ['-f', '/home/tip/tip/cli/fabfile.py', '%(id)s:%(param)s' % req.params ], { stdio: [ 0, 'pipe', 0 ]});
    child.stdout.on('data',
        function (data) {
            res.send(JSON.stringify(data.toString()));
        }
    );
});
app.get('/api/v1/:op', function(req, res) { res.send(usage); });
app.get('/api/v1/', function(req, res) { res.send(usage); });

app.listen(process.env.PORT || 8080);
