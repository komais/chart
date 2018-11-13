import numpy as np 
import pylab 
import scipy.stats as stats
import pandas as pd
import pandas
import sys
from pandas import Series,DataFrame #此两个为pandas中的数据结构，特别是DataFrame 非常实用
import glob,os
import plotly.offline as py
from plotly.graph_objs import Scatter, Layout
import pprint as pp
import calendar
import plotly.graph_objs as go 
import colorlover as cl

def MSE(s1 , s2 ):
	if isinstance(s1 , pandas.core.series.Series) and isinstance(s2 , pandas.core.series.Series):
		if len(s1) == len(s2):
			return sum((s2-s1)**2)/len(s2)
		else:
			sys.exit('two series have different elements')
	else:
		sys.exit('input should be a series')

def MAE(s1 , s2 ) :
	if isinstance(s1 , pandas.core.series.Series) and isinstance(s2 , pandas.core.series.Series):
		if len(s1) == len(s2):
			return sum(abs(s2-s1))/len(s2)
		else:
			sys.exit('two series have different elements')
	else:
		sys.exit('input should be a series')

def RMSE(s1, s2):
	return MSE(s1,s2) ** (1/2) 

def error_rate(list1 , list2):
	pass

def PN(TP,TN,FP,FN,):
	name_list = ['accuracy' , 'sensitive','specificity','precision' , 'recall','f1']
	r_dict = { i:0 for i in name_list}
	P = TP + FN
	N = FP + TN
	r_dict['accuracy'] = (TP +TN)/(P+N)
	r_dict['sensitive'] = TP / P
	r_dict['specificity'] = TN/N
	r_dict['precision'] = TP/(TP+FP)
	r_dict['recall'] = TP / P
	r_dict['f1'] = 2*r_dict['precision']*r_dict['recall']  / ( r_dict['precision'] + r_dict['recall'])
	return(r_dict)
	
def normalization(df):
	df_norm = (df - df.mean()) / (df.max() - df.min())
	return (df_norm)
