from __future__ import  division
import math

def cumdist(samples):
  """
  Computes the cummulated distance along a sequence of vectors.
  samples = [ [v11,...,v1N], ... [vn1,...,vnN] ]
  """
  N, l, Ln = len(samples), [0.0], 0.0
  for i in range(1,N):
    Li = math.sqrt( sqL2(samples[i], samples[i-1]) )
    Ln += Li
    l.append(Ln)
  return l, Ln

def sqL2(a, b):
  """
  Computes the L2 euclidean distance between two vectors.
  a = [a1,...,aN]; b = [b1,...,bN]
  """
  dim, nrg = len(a), 0.0
  for d in range(dim):
    dist = a[d] - b[d]
    nrg += dist * dist
  return nrg

def clustercenter(samples):
  """
  Computes the geometric center of a set of vectors.
  samples = [ [v11,...,v1N], ... [vn1,...,vnN] ]  
  """
  N, dim = len(samples), len(samples[0])
  if N == 1: # singleton cluster
    return samples[0]
  # Cluster center is the average in all dimensions
  dsum = [0.0] * dim
  for d in range(dim):
    for i in range(N):
      dsum[d] += samples[i][d]
    dsum[d] /= N
  return dsum

