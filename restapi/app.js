var express = require('express');
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

app.get('/api/v1/', function(req, res) {
    res.send('\
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
</html>');});

app.listen(process.env.PORT || 8080);
