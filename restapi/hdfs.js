var express = require('express');
var os = require('os');
var fs = require('fs');
var cors = require('cors');
var child_process = require('child_process');
var app = express();
var user = 'nobody';

/*
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
*/
app.use(cors());

var usage = '<html>HDFS</html>';

app.get('/webhdfs/v1/:a/:b/:c/:d', function(req, res) {
   res.writeHead(200, {'Content-Type': 'image/jpeg'});
   res.write(fs.readFileSync('/hdfs/' + req.params.a + '/' + req.params.b + '/' + req.params.c + '/' + req.params.d));
   res.end()
});

app.get('/webhdfs/v1/:a/:b/:c', function(req, res) {
   res.writeHead(200, {'Content-Type': 'image/jpeg'});
   res.write(fs.readFileSync('/hdfs/' + req.params.a + '/' + req.params.b + '/' + req.params.c));
   res.end()
});

app.get('/webhdfs/v1/:a/:b', function(req, res) {
   res.writeHead(200, {'Content-Type': 'image/jpeg'});
   res.write(fs.readFileSync('/hdfs/' + req.params.a + '/' + req.params.b));
   res.end()
});

app.get('/webhdfs/v1/:op/', function(req, res) {
    child = child_process.exec('ls /hdfs/' + req.params.op,
        function (error, stdout, stderr) {
            res.json({
                "user": user,
                "ip": req.ip,
                "request": req.originalUrl,
                "result": stdout.toString().split('\n')
            });
            if (error !== null) {
                console.log('exec error: ' + error);
            }
        });
});

app.listen(process.env.PORT || 14000);
