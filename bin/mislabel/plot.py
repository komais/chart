import numpy as np 
import pylab 
import scipy.stats as stats
import pandas as pd
import sys
from pandas import Series,DataFrame #此两个为pandas中的数据结构，特别是DataFrame 非常实用
import glob,os
import plotly.offline as py
from plotly.graph_objs import Scatter, Layout
import pprint as pp
import calendar
import plotly.graph_objs as go 
import colorlover as cl

py.init_notebook_mode(connected=True)

def qqplot(series , name):
	tt = series[pd.notna(series )]
	res = stats.probplot(tt, dist="norm", plot=pylab)
	pylab.title('qqplot of {0}'.format(name))
	pylab.show()
	slope, intercept, r = res[1]
	r_square = r * r
	return(r_square)
	##https://www.programcreek.com/python/example/1270/pylab.show pylab example

class myPlot():
	def __init__(self, df , xlabel='' , ylabel='' , title='' , color_by = '' ) :
		''' 以index为x轴，column name为y轴进行绘图，数据转换有fromat完成'''
		self.df = df
		self.xlabel = xlabel
		self.ylabel = ylabel
		self.title = title
		self.color_by = color_by


	def line_plot(self , xlabel='' , ylabel='' , title='' , x = '' , xtype='' , y=''):
		df =self.df
		if x : 
			self.xlabel = x
			x = self.df[x]
		else:
			self.xlabel = 'all_index'
			x = self.df.index
		if y : 
			self.ylabel = "&".join(y)
		else:
			y = set(df.columns.get_level_values(0))
			self.ylabel = 'all_column'
		if xlabel: self.xlabel = xlabel
		if ylabel: self.ylabel = ylabel
		if title : self.title  = title

		traces = []
		if isinstance( self.color_by ,pd.core.frame.DataFrame): 
			category = self.color_by.iloc[: , 0].unique()
			if len(category) >2:
				col_list = cl.scales[len(category)]['div']['RdYlBu']
			elif len(category) == 2:
				col_list = ['rgb(252,141,89)', 'rgb(145,191,219)']
			else:
				col_list = ['rgb(252,141,89)']
			category_dict = { j:col_list[i] for i,j in enumerate(category)}
			category_flag = { j : 0 for j in category}

		for j in y: 
			#print(df.index)
			if isinstance( self.color_by ,pd.core.frame.DataFrame):
				group_name  = self.color_by.iloc[:,0][j]
				group_color = category_dict[ group_name ] 
				if category_flag[group_name] : 
					trace_tmp=go.Scatter( 
						name= group_name ,
						x=x,
						y=df[j],
						legendgroup=group_name,
						showlegend=False,
						line = dict(color= group_color),
					)
				else:
					trace_tmp=go.Scatter( 
						name= group_name ,
						x=x,
						y=df[j],
						legendgroup=group_name,
						showlegend=True,
						line = dict(color= group_color),
					)
					category_flag[group_name] += 1 
			else:
				trace_tmp=go.Scatter( 
					name=j, 
					x=x,
					y=df[j],
				)
			traces+=[trace_tmp]
		x_axis_template=dict(
			showgrid=True,  #网格
			zeroline=True,  #是否显示基线,即沿着(0,0)画出x轴和y轴
			nticks=20,
			showline=True,
			title=self.xlabel,
			mirror='all',
			#type="category",
		)
		if xtype: x_axis_template['type'] = xtype
		
		y_axis_template=dict(
			showgrid=True,  #网格
			zeroline=True,  #是否显示基线,即沿着(0,0)画出x轴和y轴
			nticks=20,
			showline=True,
			title=self.ylabel, #y轴标题
			mirror='all'
		)
		

		layout=go.Layout(
			title=self.title,
			xaxis=x_axis_template,
			yaxis=y_axis_template
			)
		data=traces
		fig=go.Figure(
			data=data,
			layout=layout
		)
		py.iplot(fig )

	def scatter_plot(self , xlabel='' , ylabel='' , title='' , x = '' , xtype='' , y='' , alpha=1):
		df =self.df
		if x : 
			self.xlabel = x
			x = self.df[x]
		else:
			self.xlabel = 'all_index'
			x = self.df.index
		if y : 
			self.ylabel = "&".join(y)
		else:
			y = set(df.columns.get_level_values(0))
			self.ylabel = 'all_column'
		if xlabel: self.xlabel = xlabel
		if ylabel: self.ylabel = ylabel
		if title : self.title  = title

		traces = []
		if isinstance( self.color_by ,pd.core.frame.DataFrame): 
			category = self.color_by.iloc[: , 0].unique()
			if len(category) >2:
				col_list = cl.scales[len(category)]['div']['RdYlBu']
			elif len(category) == 2:
				col_list = ['rgb(252,141,89)', 'rgb(145,191,219)']
			else:
				col_list = ['rgb(252,141,89)']
			category_dict = { j:col_list[i] for i,j in enumerate(category)}
			category_flag = { j : 0 for j in category}

		for j in y: 
			#print(df.index)
			if isinstance( self.color_by ,pd.core.frame.DataFrame):
				group_name  = self.color_by.iloc[:,0][j]
				group_color = category_dict[ group_name ] 
				if category_flag[group_name] : 
					trace_tmp=go.Scatter( 
						name= group_name ,
						x=x,
						y=df[j],
						legendgroup=group_name,
						showlegend=False,
						mode = 'markers',
						marker = dict(color= group_color,opacity= alpha),
					)
				else:
					trace_tmp=go.Scatter( 
						name= group_name ,
						x=x,
						y=df[j],
						legendgroup=group_name,
						showlegend=True,
						mode = 'markers',
						marker = dict(color= group_color ,opacity= alpha),
					)
					category_flag[group_name] += 1 
			else:
				trace_tmp=go.Scatter( 
					name=j, 
					x=x,
					y=df[j],
					mode = 'markers',
					marker = dict(opacity= alpha),
				)
			traces+=[trace_tmp]
		x_axis_template=dict(
			showgrid=True,  #网格
			zeroline=True,  #是否显示基线,即沿着(0,0)画出x轴和y轴
			nticks=20,
			showline=True,
			title=self.xlabel,
			mirror='all',
			#type="category",
		)
		if xtype: x_axis_template['type'] = xtype
		
		y_axis_template=dict(
			showgrid=True,  #网格
			zeroline=True,  #是否显示基线,即沿着(0,0)画出x轴和y轴
			nticks=20,
			showline=True,
			title=self.ylabel, #y轴标题
			mirror='all'
		)
		

		layout=go.Layout(
			title=self.title,
			xaxis=x_axis_template,
			yaxis=y_axis_template
			)
		data=traces
		fig=go.Figure(
			data=data,
			layout=layout
		)
		py.iplot(fig )
