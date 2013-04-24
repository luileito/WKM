var util = require("util")
  , fs   = require("fs")
  , wkmb = require("./wkmb")
  , math = require("./mathlib")
  , args   = process.argv.slice(2)
  , n_args = args.length
  , e_args = 2    
  ;

if (n_args < e_args) {
  console.log("Usage Error: "+process.argv[0]+" file K [delta]");
  // Examples reading from stdin:
  //   echo -e '1 2 3\\n2 3 4\\n6 5 6\\n' | node main.js - 2
  //   tail -n +2 ../sensor.csv | tr ',' ' ' | node main.js - 5
  console.log("In this example, rows are data samples, columns are dimensions (separated by spaces)");
  process.exit(1);
}

var dfile = args[0]
  , num_k = args[1]
  , delta = n_args > 2 ? args[2] : 0
  ;

if (dfile === "-") {
  dfile = '/dev/stdin';
}

// Read data samples
var dseq = []
  , data
  ;

fs.readFileSync(dfile).toString().split("\n").forEach(function(line) {
  // Do some cleanup and convert data to list
  var trimmed = line.toString().trim();
  if (trimmed) {
    dseq.push( trimmed.split(" ").map(parseFloat) );
  }
});

var w = new wkmb(math.whiten(dseq), num_k, delta);
w.cluster();

console.log("boundaries:",    w.boundaries );
//console.log( "clusters:",      w.clusters);
console.log("centroids:",     w.centroids);
console.log("localenergy:",   w.localenergy);
console.log("totalenergy:",   w.totalenergy);
console.log("iterations:",    w.iterations);
console.log("numtransfers:",  w.numtransfers);
console.log("cost:",          w.cost);
