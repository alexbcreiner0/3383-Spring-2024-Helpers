import time
import copy
from matplotlib import pyplot as plt
from numpy import random as r
import sys
import os
import math
import inspect

current_directory = os.getcwd()
docstrings_dir = 'docstrings'
os.chdir(docstrings_dir)

try:
	with open('TestMachine Docstrings.txt') as docstrings_file:
		docstrings = {}
		lines = docstrings_file.readlines()
		current_line = 0
		while current_line+1 < len(lines):
			key = lines[current_line].strip()
			current_line += 1
			value = ''
			while lines[current_line].strip() != '###':
				value += lines[current_line]
				current_line += 1
			docstrings[key] = value
			current_line += 1
except OSError: 
	print('Error opening docstrings')

class TestMachine:
	def __init__(self, *algos, generator = None, n_range = (10,700), steps = 1, trials = 1, mode = 'average', clean_outliers = True):
		self.algos = list(algos)
		self.generator = generator
		self.mode = mode
		self.trials = trials
		self.n_range = n_range
		self.steps = steps
		self.history = {}
		self.clean_outliers = clean_outliers

	def add_algos(self, *algos):
		for algo in algos:
			self.algos.append(algo)

	def clear_algos(self):
		self.algos = []

	def set_generator(self, func):
		self.generator = func

	def generate(self, n):
		try:
			args = self.generator(n)
			return args
		except Exception:
			print('I would love to do some testing for you, but you havent assigned me an input generator.')

	def test(self, n):
		results = []
		test_args = self.generate(n)
		for algo in self.algos:
			if isinstance(test_args, tuple) and len(test_args) == 2:
				if isinstance(test_args[1], dict):
					test_args, test_kwargs = test_args[0], test_args[1]
					test_args_copy = tuple(test_args)
					test_kwargs_copy = tuple(test_kwargs)
					start = time.perf_counter()
					algo(*test_args_copy, **test_kwargs_copy)
					stop = time.perf_counter()
					results.append(stop-start)
					continue
			if isinstance(test_args, list):
				print(f'IOts a fucking list')
				test_args_copy = copy.copy(test_args)
				start = time.perf_counter()
				algo(test_args_copy)
				stop = time.perf_counter()
				results.append(stop-start)
				continue
			if isinstance(test_args, tuple):
				test_args_copy = copy.copy(test_args)
				start = time.perf_counter()
				algo(*test_args_copy)
				stop = time.perf_counter()
				results.append(stop-start)
				continue
			test_args_copy = copy.copy(test_args)
			start = time.perf_counter()
			algo(*test_args_copy)
			stop = time.perf_counter()
			results.append(stop-start)
		return results

	def multi_test(self, n, trials = None):
		if trials == None: trials = self.trials
		results = []
		for algo in self.algos:
			results.append([])
		for i in range(trials):
			trial_times = self.test(n)
			print(f'trial_times: {trial_times}')
			for i,algo in enumerate(self.algos):
				results[i].append(trial_times[i])
		return results

	def __str__(self):
		s = f'I am a testing machine with the following attributes: \n'
		s += f'Algorithms to test: {self.algos}\n'
		s += f'Generator to use: {self.generator}\n'
		s += f'n ranges from {self.n_range[0]} to {self.n_range[1]}\n'
		s += f'Step size is {self.steps}\n'
		s += f'Number of tests per sample size is {self.trials}\n'
		s += f'In {self.mode} mode\n'
		s += f'Deleting outliers: {self.clean_outliers}'
		return s

	def test_run(self, n, trials = None, mode = None):
		if trials == None: trials = self.trials
		if mode == None: mode = self.mode
		results = self.multi_test(n= n, trials= trials)
		compiled_times = []
		if mode == 'average':
			for i in results:
				total = 0
				for time in i:
					total += time
				compiled_times.append(total/trials)
			return compiled_times
		elif mode == 'worst':
			for i in results:
				worst = -1*math.inf
				for time in i:
					if time > worst: worst = time
				compiled_times.append(worst)
			return compiled_times
		elif mode == 'best':
			for i in results:
				best = math.inf
				for time in i:
					if time < best: best = time
				compiled_times.append(best)
			return compiled_times

	def full_test(self, trials = None, n_range = None, steps = None, clean_outliers = None, mode = None):
		if trials == None: trials = self.trials
		if n_range == None: n_range = self.n_range
		if steps == None: steps = self.steps
		if clean_outliers == None: clean_outliers = self.clean_outliers
		if mode == None: mode = self.mode
		times = []
		totals = []
		for algo in self.algos:
			times.append([])
			totals.append(0)
		for n in range(self.n_range[0],self.n_range[1],self.steps):
			if n%100 == 0: print(f'n is currently {n}')
			compiled_times = self.test_run(n, trials)
			for i in range(len(self.algos)):
				totals[i] += compiled_times[i]
				if compiled_times[i] > 5*totals[i]:
					times[i].append(times[i][n-1])
				else:
					times[i].append(compiled_times[i])
		return times

	def full_test_and_plot(self, trials = None, n_range = None, steps = None, labels = None, mode = None):
		if trials == None: trials = self.trials
		if n_range == None: n_range = self.n_range
		if steps == None: steps = self.steps
		if mode == None: mode = self.mode
		times = self.full_test(trials, n_range, steps)
		x_axis = [n for n in range(n_range[0],n_range[1],steps)]
		if labels == None:
			labels = []
			for i, algo in enumerate(self.algos):
				labels.append(algo.__name__)
		fig, ax = plt.subplots()
		for i,algo in enumerate(self.algos):
			ax.plot(x_axis, times[i], label=labels[i])
		ax.legend()
		plt.show()	

stuff = dict(inspect.getmembers(TestMachine))
for name in docstrings:
	if name in stuff:
		stuff[name].__doc__ = docstrings[name]
os.chdir(current_directory)

if __name__ == '__main__':
	from testing_utilities import *
	from karatsuba import *
	from generators  import *
	from sorting_algos import *
	T = TestMachine(heapsort, quicksort, generator = list_exponential)
	T.n_range = (10,300)
	T.full_test_and_plot()