var express = require('express');
var os = require('os');
var cors = require('cors');
var child_process = require('child_process');
var path = require('path');
var app = express();
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'jade');
var nodecache = require('node-cache');
var cache = new nodecache();
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

app.get('/api/v1/:op/:param', function (req, res) {
    console.log(user + "@" + req.ip + ": " + req.originalUrl);
    console.log('/usr/local/bin/fab -f ../cli/fabfile.py ' + req.params.op + ':' + req.params.param);

    value = cache.get( req.originalUrl );
    if (value == undefined) {
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
                } else {
                    obj = { my: "Special", variable: 42 };
                    success = cache.set( req.originalUrl, stdout.toString(), 10000 );
                }
            });
    } else {
        console.log('Use Cache: ' + value);
        res.setHeader('Access-Control-Allow-Origin', '*');
        res.json({
            "user": user,
            "ip": req.ip,
            "request": req.originalUrl,
            "result": value
        });
    }
});

app.get('/api/v1/:op', function (req, res) {
    res.redirect('/api/v1/');
});

app.get('/api/v1/', function (req, res) {
    var fs = require('fs');
    var fab_help = fs.readFileSync('./fab_help.txt', 'utf8');
    var fab_modules = new Array();
    var fab_lines = fab_help.split("\n");

    for (index = 2; index < fab_lines.length; index++) {
        var fab_line = fab_lines[index].trim().split("fab ");
        var fab_command = String(fab_line[0]).trim();
        var fab_parameter = String(fab_line[1]).replace(fab_command + ":", "").trim();
        var fab_url = "/api/v1/" + fab_command + "/" + encodeURIComponent(fab_parameter);
        console.log(fab_command + " --> " + fab_parameter);

        if (fab_command.length > 0) {
            fab_modules.push({'name': fab_command, 'parameter': fab_parameter, 'url': fab_url});
        }
    }

    res.render('index', {fab_modules: fab_modules});
});

app.listen(process.env.PORT || 5555);
