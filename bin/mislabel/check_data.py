import pandas as pd
import numpy as np
import sys
from pandas import Series,DataFrame #此两个为pandas中的数据结构，特别是DataFrame 非常实用
import glob,os
import plotly.offline as py
from plotly.graph_objs import Scatter, Layout
import pprint as pp
import calendar
import plotly.graph_objs as go 
import collections
py.init_notebook_mode(connected=True)


def shape(df):
	row, column = df.shape
	print("该数据有{0}个实例(样品)，{1}个属性(维度)".format(row, column))
	
	#df.describe(percentiles=[.05, .25, .75, .95])

def feature_type(df):
	r_dict = collections.OrderedDict()
	for i in ['col' , 'name', 'type', 'length' , 'NA_count' , 'missing_rate' , 'range' , 'information'] :
		r_dict[i]=[]
	count = 0 
	for col_name in df:
		a_col = df[ col_name ] 
		r_dict['col'].append(count)
		r_dict['name'].append(col_name)
		if isinstance( a_col[0] , float):
			r_dict['type'].append('float')
			r_dict['range'].append('{0:.2f},{1:.2f}'.format(a_col.min(), a_col.max()))
			tt = a_col.quantile([.25, .5, .75])
			r_dict['information'].append("{0:.2f},{1:.2f},{2:.2f}".format(tt.iloc[0] , tt.iloc[1], tt.iloc[2]))
		elif isinstance( a_col[0] , str):
			r_dict['type'].append('string')
			category = a_col.unique()
			#print(category)
			r_dict['range'].append(','.join( category ) )
			r_dict['information'].append(",".join([str(a_col.value_counts()[i]) for i in category]))
		else:
			sys.exit( '{0} is not float or string, is {1}'.format(col_name , type(a_col[0])))
		r_dict['length'].append(len(a_col))
		r_dict['NA_count'].append( sum(pd.isna(a_col)))
		r_dict['missing_rate'].append ( sum(pd.isna(a_col)) / len(a_col) * 100)
		count += 1
	#for i in r_dict:
		#print(len(r_dict[i]))
	return(pd.DataFrame(r_dict))



