(function(module, global){

  var Mathlib = {
  
    /**
     * Computes the cummulated distance along a sequence of vectors.
     * @param samples Array [ [v11,...,v1N], ... [vn1,...,vnN] ]
     * @return {{ values: Array, length: Number }}
     */
    cumdist: function(samples) {
      var N = samples.length, l = [0], Ln = 0;
      for (var i = 1; i < N; i++) {
        var Li = Math.sqrt( this.sqL2(samples[i], samples[i-1]) );
        Ln += Li;
        l.push(Ln);
      }
      return { values:l, length:Ln };
    },

    /**
     * Computes the L2 euclidean distance between two vectors.
     * @param a Array [a1,...,aN]
     * @param a Array [b1,...,bN]
     * @return Number
     */
    sqL2: function(a, b) {
      var dim = a.length, nrg = 0;
      for (var d = 0; d < dim; d++) {
        var dist = a[d] - b[d];
        nrg += dist * dist;
      }
      return nrg;
    },

    /**
     * Computes the geometric center of a set of vectors.
     * @param samples Array [ [v11,...,v1N], ... [vn1,...,vnN] ]
     * @return Array
     */
    clustercenter: function(samples) {
      var N = samples.length, dim = samples[0].length, dsum = [];
      if (N === 1) { // singleton cluster
        return samples[0];
      }
      // Cluster center is the average in all dimensions
      for (var d = 0; d < dim; d++) {
        dsum[d] = 0;
        for (var i = 0; i < N; i++) {
          dsum[d] += samples[i][d];
        }
        dsum[d] /= N;
      }
      return dsum;
    },
    
    /**
     * Divides each feature by its standard deviation across all observations, 
     * in order to give it unit variance.
     * @param samples Array [ [v11,...,v1N], ... [vn1,...,vnN] ]
     * @return Array
     */
    whiten: function(samples) {
      var N = samples.length, dim = samples[0].length, pts = samples.slice();
      for (var d = 0; d < dim; d++) {
        var i, col = [];
        for (i = 0; i < N; i++) {
          col.push(samples[i][d]);
        }
        var o = this.msd(col);
        if (o.sd > 0) for (i = 0; i < N; ++i) {
          pts[i][d] /= o.sd;
        }
      }
      return pts;
    },
    
    /**
     * Computes the sum of all vector values.
     * @paran vec Array [v1,...,vN]
     * @return Number
     */
    sum: function(vec) {
      var n = vec.length, sum = 0;
      for (var d = 0; d < n; d++) {
        sum += vec[d];
      }
      return sum;
    },
    
    /**
     * Computes the average of all vector values.
     * @paran vec Array [v1,...,vN]
     * @return Number
     */
    avg: function(vec) {
      return this.sum(vec)/vec.length;
    },
    
    /**
     * Computes the mean plus standard deviation of a vectors.
     * @paran vec Array [v1,...,vN]
     * @return {{ mean: Number, sd: Number }}
     */
    msd: function(vec) {
      var m = this.avg(vec), s = 0, n = vec.length;
      if (n > 1) {
        for (var d = 0; d < n; d++) {
          var dist = vec[d] - m;
          s += dist * dist;
        }
        s = Math.sqrt(s / (n-1));
      }
      return { mean: m, sd: s };
    }
    
  };

  module.exports = Mathlib;

})('object' === typeof module ? module : {}, this);
