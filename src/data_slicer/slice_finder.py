

import pickle
import numpy as np
import pandas as pd
import functools
import copy
import concurrent.futures
from sklearn.metrics import log_loss, accuracy_score
from scipy import stats


from .risk_control import *

"""
	Slice is specified with a dictionary that maps a set of attributes 
	and their values. For instance, '1 <= age < 5' is expressed as {'age':[[1,5]]}
	and 'gender = male' as {'gender':[['male']]}
"""
class Slice:
	def __init__(self, slice_des, slice_index):
		self.slice_des = slice_des		
		self.slice_index = slice_index		# list of index of data in slice
		self.size = len(slice_index)		# size of slice
		self.eff_size = None				#
		self.metric = None					#


	def set_metric(self, metric):
		self.metric = metric

	def set_effect_size(self, effect_size):
		self.effect_size = effect_size


	def join(self, s):

		des = self.slice_des
		for key, value in list(s.slice_des.items()):
			if key not in des:
				des[key] = value  # add from s which was not in self

			else: 
				for limit in s.slice_des[key]:
					if limit not in des[key]:
						des[key].append(limit)

		index = self.slice_index.intersection(s.slice_index)
		item = Slice(des, index)

		return item



	def __str__(self):
		desc = ''
		for key in self.slice_des.keys():
			desc += ' ' + str(key) + ' : ' + str(self.slice_des[key])
		return desc

	def discript_html(self):

		out = []
		for k, v in list(self.slice_des.items()):
			out.append(str(k) + " : " + str(v))

		out.append("Size" + " : " + str(self.size))

		return out










class SliceFinder:
	def __init__(self, data,y_pred, model_classes):
		self.model_classes = model_classes
		self.data = data

		self.predict = y_pred

	def find_slice(self, k=50, epsilon=0.2, degree=3, max_workers=1):
		''' Find interesting slices '''

		assert k > 0, 'Number of recommendation k should be greater than 0'

		metrics_all = self.evaluate_model(self.data[0].index)
		reference = (np.mean(metrics_all), np.std(metrics_all), len(metrics_all))

		slices = []
		uninteresting = []
		for i in range(1,degree+1):
			print('degree %s'%i)
			# degree 1~3 feature crosses
			print ('slicing')
			if i == 1:
				candidates = self.slicing()
			else:
				candidates = self.crossing(uninteresting, i)
			print ('effect size filtering')
			interesting, uninteresting_ = self.filter_by_effect_size(candidates, reference, epsilon, 
																	max_workers=max_workers)
			uninteresting += uninteresting_
			slices += interesting
			if len(slices) >= k:
				break

		print ('sorting')
		slices = sorted(slices, key=lambda s: s.size, reverse=True)
		return slices[:k]
			
	def slicing(self):
		''' Generate base slices '''
		X, y = self.data[0], self.data[1]
		n, m = X.shape[0], X.shape[1]

		slices = []
		for col in X.columns:
			uniques, counts = np.unique(X[col], return_counts=True)
			if len(uniques) == n:
				# Skip ID like col
				continue
			if len(uniques) > n/2.:
				# Bin high cardinality col
				bin_edges = self.binning(X[col], n_bin=10)
				for i in range(len(bin_edges)-1):
					slice_index= X[ np.logical_and(bin_edges[i] <= X[col], X[col] < bin_edges[i+1]) ].index
					s = Slice({col:[[bin_edges[i],bin_edges[i+1]]]}, slice_index)
					slices.append(s)
			else:
				for v in uniques:
					slice_index = X[X[col] == v].index
					s = Slice({col:[[v]]}, slice_index)                 
					slices.append(s)

		return slices

	def crossing(self, slices, degree):
		print("#######################")
		''' Cross uninteresting slices together '''
		crossed_slices = []
		for i in range(len(slices)-1):
			for j in range(i+1, len(slices)):
				if len(slices[i].slice_des) + len(slices[j].slice_des) == degree:
					
					crossed_slices.append(slice_ij.join(slices[j]))
		return crossed_slices



	def evaluate_model(self, data_index, metric=log_loss):
		''' evaluate model on a given data (X, y), example by example '''

		y = self.data[1].loc[data_index]
		y_p = self.predict.loc[data_index]
		y_p = list(map(functools.partial(np.expand_dims, axis=0), y_p))
		y = list(map(functools.partial(np.expand_dims, axis=0), y))
		if metric == log_loss:
			return list(map(functools.partial(metric, labels=self.model_classes), y, y_p))
		elif metric == accuracy_score:
			return list(map(metric, y, y_p))

	def filter_by_effect_size(self, slices, reference, epsilon=0.5, max_workers=1):
		''' Filter slices by the minimum effect size '''
		filtered_slices = []
		rejected = []

		with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
			batch_jobs = []
			for s in slices:
				if s.size == 0:
					continue
				batch_jobs.append(executor.submit(self.eff_size_job, s, reference))
			for job in concurrent.futures.as_completed(batch_jobs):
				if job.cancelled():
					continue
				elif job.done():
					s = job.result()
					if s.effect_size >= epsilon:
						#if risk_control is False or test_result:
						filtered_slices.append(s)
					else:
						rejected.append(s)
		return filtered_slices, rejected

	def eff_size_job(self, s, reference):
		m_slice = self.evaluate_model(s.slice_index)
		eff_size = effect_size(m_slice, reference)

		s.set_metric(np.mean(m_slice))
		s.set_effect_size(eff_size)
		return s  #, test_result
	


	def binning(self, col, n_bin=20):
		''' Equi-height binning '''
		bin_edges = stats.mstats.mquantiles(col, np.arange(0., 1.+1./n_bin, 1./n_bin))
		return bin_edges
