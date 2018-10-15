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
py.init_notebook_mode(connected=True)


def stat(df):
	df.shape()
	df.describe(percentiles=[.05, .25, .75, .95])



