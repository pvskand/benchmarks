'''
  @file ann.py

  Class to benchmark the MRPT Approximate Nearest Neighbors method.
'''

import os
import sys
import inspect

# Import the util path, this method even works if the path contains symlinks to
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from log import *
from timer import *
from misc import *
import numpy as np

import mrpt

'''
This class implements the Approximate K-Nearest-Neighbors benchmark.
'''
class ANN(object):

  '''
  Create the Approximate K-Nearest-Neighbors benchmark instance.

  @param dataset - Input dataset to perform Approximate K-Nearest-Neighbors on.
  @param timeout - The time until the timeout. Default no timeout.
  @param verbose - Display informational messages.
  '''
  def __init__(self, dataset, timeout=0, verbose=True):
    self.verbose = verbose
    self.dataset = dataset
    self.timeout = timeout

  '''
  Use the MRPT libary to implement Approximate Nearest-Neighbors.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def AnnMrpt(self, options):
    def RunAnnMrpt(q):
      totalTimer = Timer()

      # Load input dataset.
      Log.Info("Loading dataset", self.verbose)
      referenceData = np.genfromtxt(self.dataset[0], delimiter=',')
      queryData = np.genfromtxt(self.dataset[1], delimiter=',')
      train, label = SplitTrainData(self.dataset)

      # Get all the parameters.
      k = re.search("-k (\d+)", options)
      n = re.search("-n (\d+)", options) # Number of trees.
      d = re.search("-d (\d+)", options) # The tree depth.
      v = re.search("-v (\d+)", options) # Number of votes_required.

      if not k:
        Log.Fatal("Required option: Number of furthest neighbors to find.")
        q.put(-1)
        return -1
      else:
        k = int(k.group(1))
        if (k < 1 or k > referenceData.shape[0]):
          Log.Fatal("Invalid k: " + k.group(1) + "; must be greater than 0"
            + " and less or equal than " + str(referenceData.shape[0]))
          q.put(-1)
          return -1
      if not n:
          Log.Fatal("Required option: Number of trees to build")
          q.put(-1)
          return -1
      else:
          n=int(n.group(1))

      d = 5 if not d else int(d.group(1))
      v = 4 if not v else int(v.group(1))

      with totalTimer:
        try:
          # Perform Approximate Nearest-Neighbors.
          acc = 0
          index = mrpt.MRPTIndex(np.float32(train), depth=d, n_trees=n)
          index.build()
          approximate_neighbors = np.zeros((len(queryData), k))
          for i in range(len(queryData)):
              approximate_neighbors[i] = index.ann(np.float32(queryData[i]), k,
                  votes_required=v)
        except Exception as e:
          Log.Info(e)
          q.put(-1)
          return -1

      time = totalTimer.ElapsedTime()
      q.put(time)
      return time

    return timeout(RunAnnMrpt, self.timeout)

  '''
  Perform Approximate K-Nearest-Neighbors. If the method has been successfully
  completed return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def RunMetrics(self, options):
    Log.Info("Perform Approximate Nearest Neighbours.", self.verbose)
    results = None
    if len(self.dataset) >= 2:
      results = self.AnnMrpt(options)

    if results < 0:
      return results

    return {'Runtime' : results}
