import sys
from wkmb import WKM
from mathlib import whiten

args = sys.argv[1:]
n_args = len(args)
e_args = 2

if n_args < e_args:
  print "Usage Error: python %s file K [delta]" % sys.argv[0]
  # Examples reading from stdin:
  #   echo -e '1 2 3\\n2 3 4\\n6 5 6\\n' | python main.py - 2
  #   tail -n +2 ../sensor.csv | tr ',' ' ' | python main.py - 5
  print "In this example, rows are data samples, columns are dimensions (separated by spaces)"
  sys.exit(1)

dfile = args[0]
num_k = args[1]
delta = args[2] if n_args > 2 else 0.0

# Read data samples
data = sys.stdin.readlines() if (dfile == "-") else file(dfile)
# Do some cleanup and convert data to list
dseq = [ map(float, line.strip().split()) for line in data if line.strip() ]

w = WKM(whiten(dseq), num_k, delta)
w.cluster()

print "boundaries:",    w.boundaries
#print "clusters:",      w.clusters
print "centroids:",     w.centroids
print "localenergy:",   w.localenergy
print "totalenergy:",   w.totalenergy
print "iterations:",    w.iterations
print "numtransfers:",  w.numtransfers
print "cost:",          w.cost
