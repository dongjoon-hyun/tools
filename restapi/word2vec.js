var express = require('express');
var os = require('os');
var cors = require('cors');
var child_process = require('child_process');
var path = require('path');
var fs = require('fs');
var math = require('mathjs');
var app = express();
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'jade');
var user = 'nobody';

app.use(cors());

var words = [];
var vectors = [];
var norms = [];

//Read word vectors from file
if(words.length == 0) {
	var fs = require('fs'), readline = require('readline');

	var rd = readline.createInterface({
		input : fs.createReadStream('./hani-vectors.txt'),
		output : process.stdout,
		terminal : false
	});

	rd.on('line', function(line) {
		var tokens = line.trim().split(" ");
		if(tokens.length < 3) {
			return;
		}
	    var word = tokens[0];
	    var vec = [];
	    for(j=1; j<tokens.length; j++) {
	    	vec.push(parseFloat(tokens[j]));
	    }
	    words.push(word);
	    vectors.push(vec);
	    norms.push(math.norm(vec));
	}).on('close', function() {
		console.log("Loading Completed: " + words.length + " words..");
	});
}

app.get('/api/v1/word2vec/qa/:param', function(req, res) {
	console.log(user + "@" + req.ip + ": " + req.originalUrl);
	console.log(req.params.param);
	console.log(words.length + ", " + vectors.length);
	
	// Split param into hint words
	var inputwords = req.params.param.split(",");
	var hint1 = inputwords[0] + "/NNP";
	var hint2 = inputwords[1] + "/NNP";
	var hint3 = inputwords[2] + "/NNP";
	var index1 = -1, index2 = -1, index3 = -1;
	var oov = [0, 0, 0];
	var times = [];
	
	times.push(Date.now());
	
	// Get hint word indexes for hint vectors
	for(i in words) {
		if(words[i].trim() == hint1.trim()) {
			index1 = i;
			oov[0] = 1;
		}
		if(words[i].trim() == hint2.trim()) {
			index2 = i;
			oov[1] = 1;
		}
		if(words[i].trim() == hint3.trim()) {
			index3 = i;
			oov[2] = 1;
		}
	}
	
	for(i in oov) {
		if(oov[i] == 0) {
			result = {'out of vocabulary': inputwords[i]}
			res.charset = 'utf-8';
		    res.contentType('text');
		    res.send(JSON.stringify(result));
		    return;
		}
	}
	
	console.log(words[index1] + ": " + vectors[index1]);
	console.log(words[index2] + ": " + vectors[index2]);
	console.log(words[index3] + ": " + vectors[index3]);
	
	times.push(Date.now());
	
	// Calculate answer vector from hint vectors
	var ansvec = [];
	for(i in vectors[index1]) {
		var v = vectors[index2][i] - vectors[index1][i] + vectors[index3][i];
		ansvec.push(v);
	}
	var normansvec = math.norm(ansvec);
	
	console.log("Ansvec: " + ansvec);
	
	times.push(Date.now());
	
	var matwords = math.matrix(vectors);
	var distvectors = math.multiply(matwords, ansvec).valueOf();
	
	times.push(Date.now());
	
	// Calculate distances from answer vector to all other word vectors
	var distances = [];
	for(i in vectors) {
		var dist = distvectors[i];
		var normwordvec = norms[i];
		distances[i] = dist / normansvec / normwordvec;
	}
	
	times.push(Date.now());
	
	// Get Top N words and vectors
	var topindexes = [0, 0, 0, 0, 0];
	var topn = [0, 0, 0, 0, 0]
	var best = 0;
	for(i in distances) {
		for(j in topn) {
			if(distances[i] > topn[j] && i != index1 && i != index2 && i != index3) {
				for(k=topn.length - 1; k>=j+1; k--) {
					topn[k] = topn[k - 1];
					topindexes[k] = topindexes[k - 1];
				}
				topn[j] = distances[i];
				topindexes[j] = i;
				break;
			}
		}
	}
	
	times.push(Date.now());
	for(t in times) {
		if(t > 0) {
			console.log(times[t] - times[t-1] + "ms");
		}
	}
	
	// Show result
	var result = {};
	for(i in topn) {
		var w = words[topindexes[i]];
		var d = topn[i];
		console.log(w + ": " + d);
		result[w] = d;
	}
	res.charset = 'utf-8';
    res.contentType('text');
    res.send(JSON.stringify(result));
});


app.listen(process.env.PORT || 5666);
