import math
from mathlib import cumdist, sqL2, clustercenter

class WKM:
  """
  Warped K-Means: an algorithm to cluster sequentially-distributed data.
  Luis A. Leiva and Enrique Vidal. Information Sciences, 2013.
  See http://dx.doi.org/10.1016/j.ins.2013.02.042
  Implemented by Luis A. Leiva.
  Dual licensed under the MIT and GPL licenses.
  Project page: http://personales.upv.es/luileito/wkm/
  """
  
  def __init__(self, samples, numclusters, threshold=0.0):
    """
    Instantiate the class.
    Threshold is the cluster population that will be tested in each iteration.
    """
    self.maxiter = 100
    # User input
    self.samples     = samples
    self.numclusters = int(numclusters)
    self.threshold   = float(threshold)
    # Assume that all samples have the same dimensions
    self.dimensions = len(self.samples[0])
    # Sanitize user input
    if self.numclusters < 1:
      self.numclusters = 1
    elif self.numclusters > len(samples):
      self.numclusters = len(samples)
    if threshold > 1:
      self.threshold = 1.0
    elif threshold < 0:
      self.threshold = 0.0
    self.reset()


  def reset(self):
    """Clean up."""
    self.initialized  = False
    # System ouput
    self.boundaries   = [0] * self.numclusters
    self.clusters     = [0] * self.numclusters
    self.centroids    = [0] * self.numclusters
    self.localenergy  = [0] * self.numclusters
    self.totalenergy  = 0.0 # FIXME: actually it can be computed as array sum of localenergy
    self.iterations   = 0
    self.numtransfers = 0
    self.cost         = 0


  def init(self, method=None):
    """Initialization method."""
    self.reset()
    N, M = len(self.samples), self.numclusters
    # Silly checks
    if self.numclusters <= 1: # single partition
      self.boundaries = [0]
      return  
    elif self.numclusters >= N: # singleton clusters
      self.boundaries = [i for i in range(N)]
      return
    # Finally check user-defined method
    if method == None:
      self.initdefault(N,M)
    else:
      m = method.lower() 
      if m == "ts":
        self.TS(N,M)
      elif m == "eq":
        self.resample(N,M)
      else: 
        self.initdefault(N,M)


  def initdefault(self, N, M):
    """
    Default boundaries initialization. 
    Will use TS only if 2M <= N (~ Nyquist).
    Other methods may be implemented, as long as they process samples in a sequential fashion.
    """
    self.boundaries = []
    if N/float(M) < 2:
      self.resample(N,M)
    else:
      self.TS(N,M)
    self.resample(N,M)
    
    
  def TS(self, N, M):
    """
    Initialize boundaries by trace segmentation (non-linear allocation). 
    This is the pre-set initialization mode.
    """
    self.boundaries = []
    Lcum, LN = cumdist(self.samples)
    incr, i = LN / float(M), 0
    for j in range(1,M+1):
      fact = (j - 1)*incr
      while fact > Lcum[i] or i in self.boundaries:
        i += 1
      self.boundaries.append(i) 
    self.initialized = True
    
    
  def resample(self, N, M):
    """Allocate N points into M boundaries in a linear fashion (see t8 APP)."""
    self.boundaries = []
    b = -1
    for i in range(N):
      q = math.floor( (i+1)*M/(N+1.0) )
      if q > b:
        b = q
        self.boundaries.append(i)
    self.initialized = True
    

  def getPartition(self):
    """Assign points to a cluster in a sequential fashion."""
    for j in range(self.numclusters):
      self.clusters[j] = self.getClusterSamples(j)
      assert len(self.clusters[j]) > 0, "Empty cluster %d" % j


  def getClusterSamples(self, index):
    """Retrieve points by cluster index."""
    l = self.boundaries[index+1] if (index+1 < self.numclusters) else len(self.samples)
    return self.samples[self.boundaries[index]:l]


  def setPartition(self, partition):
    """Specify a sequential cluster configuration."""
    self.boundaries, self.clusters = [0], []
    for j, points in enumerate(partition):
      assert len(points) > 0, "Empty cluster %d" % j
      self.clusters[j] = points
      if j > 0:
        self.boundaries.append(len(points)-1)


  def computeEnergies(self):
    """Compute the energy of all clusters from scratch."""
    self.totalenergy = 0.0
    for j in range(self.numclusters):
      points = self.clusters[j]
      assert len(points) > 0, "Empty cluster %d" % j
      self.centroids[j] = clustercenter(points)
      energy = 0.0
      for pt in points:
        energy += sqL2(pt, self.centroids[j])
      self.localenergy[j] = energy
      self.totalenergy += energy


  def incrementalMeans(self, sample, j, bestcluster, n, m):
    """Recompute cluster means as a result of reallocating a sample."""
    newj = [0.0] * self.dimensions
    newbest = newj[:]
    for d in range(self.dimensions):
      newbest[d] = self.centroids[bestcluster][d] + (sample[d] - self.centroids[bestcluster][d]) / (m+1.0)
      newj[d] = self.centroids[j][d] - (sample[d] - self.centroids[j][d]) / (n-1.0)
    self.centroids[bestcluster] = newbest
    self.centroids[j] = newj
    

  def cluster(self, partition=None):
    """Perform sequential clustering."""
    if not self.initialized:
      self.init()
    if partition:
      self.setPartition(partition)
    else:
      self.getPartition()
    self.computeEnergies()
    # Silly check
    if self.numclusters < 2:
      return
    # Reallocate boundaries
    while True:
      transfers = False # no transfers yet
      for j in range(self.numclusters):
        points = self.clusters[j]
        n = len(points)
        if n < 2: continue
        # Otherwise explore 1st half
        if j > 0: 
          for i in range(0, int(math.floor(n/2.0 * (1 - self.threshold))) + 1):
            sample = points[i]
            bestcluster = j-1
            m = len(self.clusters[bestcluster])
            n = len(self.clusters[j])
            J1 = (m / (m + 1.0)) * sqL2(sample, self.centroids[bestcluster])
            J2 = (n / (n - 1.0)) * sqL2(sample, self.centroids[j])
            delta = J1 - J2
            self.cost += 1
            if delta < 0 and n > 1:
              transfers = True
              self.numtransfers += 1
              self.boundaries[j] += 1
              # Recompute means incrementally
              self.incrementalMeans(sample,j,bestcluster,n,m)
              # Recompute local energies
              self.localenergy[bestcluster] += J1
              self.localenergy[j] -= J2
              # Overall energy simply decreases
              self.totalenergy += delta
              self.getPartition()
            else: break
        points = self.clusters[j]
        n = len(points)
        if n < 2: continue
        # Otherwise explore 2nd half
        if j + 1 < self.numclusters:
          for i in range(n-1, int(math.floor(n/2.0 * (1 + self.threshold))) - 2, -1):
            sample = points[i]
            bestcluster = j+1
            m = len(self.clusters[bestcluster])
            n = len(self.clusters[j])
            J1 = (m / (m + 1.0)) * sqL2(sample, self.centroids[bestcluster])
            J2 = (n / (n - 1.0)) * sqL2(sample, self.centroids[j])
            delta = J1 - J2
            self.cost += 1
            if delta < 0 and n > 1:
              transfers = True
              self.numtransfers += 1
              self.boundaries[bestcluster] -= 1
              # Recompute means incrementally
              self.incrementalMeans(sample,j,bestcluster,n,m)
              # Recompute local energies
              self.localenergy[bestcluster] += J1
              self.localenergy[j] -= J2
              # Overall energy simply decreases
              self.totalenergy += delta
              self.getPartition()
            else: break
      # Update
      self.iterations += 1
      if not transfers or self.iterations == self.maxiter: break
    # Finally, recompute energies from scratch when algorithm converges, to avoid rounding errors
    self.computeEnergies()

