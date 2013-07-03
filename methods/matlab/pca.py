'''
  @file pca.py
  @author Marcus Edel

  Class to benchmark the matlab Principal Components Analysis method.
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
from profiler import *

import shlex
import subprocess
import re
import collections

'''
This class implements the Principal Components Analysis benchmark.
'''
class PCA(object):

	''' 
	Create the Principal Components Analysis benchmark instance.
  
  @param dataset - Input dataset to perform PCA on.
  @param path - Path to the mlpack executable.
  @param verbose - Display informational messages.
	'''
	def __init__(self, dataset, path="/opt/matlab/bin/", verbose=True): 
		self.verbose = verbose
		self.dataset = dataset
		self.path = path

	'''
	Destructor to clean up at the end.
	'''
	def __del__(self):		
		pass	
		
	'''
  Perform Principal Components Analysis. If the method has been successfully 
  completed return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or -1 if the method was not successful.
  '''
	def RunMethod(self, options):
		Log.Info("Perform PCA.", self.verbose)

		inputCmd = "-i " + self.dataset + " " + options
		# Split the command using shell-like syntax.
		cmd = shlex.split(self.path + "matlab -nodisplay -nosplash -r \"try, pca('" 
				+ inputCmd + "'), catch, exit(1), end, exit(0)\"")
		
		# Run command with the nessecary arguments and return its output as a byte
		# string. We have untrusted input so we disables all shell based features.
		try:
			s = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=False)		
		except Exception, e:
			print e
			Log.Fatal("Could not execute command: " + str(cmd))
			return -1

		# Return the elapsed time.
		timer = self.parseTimer(s)
		if not timer:
			Log.Fatal("Can't parse the timer")
			return -1
		else:
			time = self.GetTime(timer)
			Log.Info(("total time: %fs" % time), self.verbose)

			return time

	'''
	Parse the timer data form a given string.

	@param data - String to parse timer data from.
	@return - Namedtuple that contains the timer data.
	'''
	def parseTimer(self, data):
		# Compile the regular expression pattern into a regular expression object to
		# parse the timer data.
		pattern = re.compile(r"""
				.*?loading_data: (?P<loading_time>.*?)s.*?
				.*?total_time: (?P<total_time>.*?)s.*?
				""", re.VERBOSE|re.MULTILINE|re.DOTALL)
		
		match = pattern.match(data)
		if not match:
			Log.Fatal("Can't parse the data: wrong format")
			return -1
		else:
			# Create a namedtuple and return the timer data.
			timer = collections.namedtuple("timer", ["loading_time", "total_time"])
			
			return timer(float(match.group("loading_time")),
					float(match.group("total_time")))

	'''
	Return the elapsed time in seconds.

	@param timer - Namedtuple that contains the timer data.
	@return Elapsed time in seconds.
	'''
	def GetTime(self, timer):
		time = timer.total_time - timer.loading_time
		return time