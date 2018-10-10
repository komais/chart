import pandas as pd
import numpy as np
import sys
from pandas import Series,DataFrame #此两个为pandas中的数据结构，特别是DataFrame 非常实用
import glob,os
import plotly.offline as py
from plotly.graph_objs import Scatter, Layout
import pprint as pp
import plotly.graph_objs as go 
py.init_notebook_mode(connected=True)

'''条目的增减，人员增减'''

def get_title(pathway , sheet_index):
	''' 输入是一个路径，下面包含xlsx， 返回第一个excel的指定的sheet的titile'''
	all_files = glob.glob("{0}/*.xlsx".format(pathway))  #文件存储路径
	#print(all_files)
	title=pd.read_excel(all_files[0],sheet_name = sheet_index).columns[3:] #读取目标列，这里从第4列开始
	title=Series(title)
	return( all_files , title)

def get_date(name,df):
	''' 检查每个文件的日期格式， 格式为 8-1 ，返回month，week'''
	if "日期（格式“月-周次”）" in df.columns:
		date=list(set(list(df["日期（格式“月-周次”）"])))
	elif "日期" in df.columns:
		date=list(set(list(df["日期"])))
	else:
		print("日期 or 日期（格式“月-周次”）")
		sys.exit()
	#print(date)
	if len(date) == 1:
		month=int(date[0].split("-")[0])
		week=int(date[0].split("-")[1])
		#date_title="".join([month,"月第",week,"周"])
	else:
		print("日期列包含的日期，不唯一，请修改！{0}:{1}".format(name,date))
		sys.exit(1)
	return month, week

def read_xlsx(all_files , sheet_index):
	''' 读取所有文件指定的sheet，返回二位字典，以month->week 为key， value为dataframe'''
	r_dict={}
	for f in all_files:
		df=pd.read_excel(f,sheet_name= sheet_index ) #默认读取表格第一个sheet，如果想跟换为第二个sheet，可以更改为：sheet_name=1
		df=df.fillna(0)
		name=os.path.split(f)[1]
		month , week =get_date(name,df)
		#print (date)
		if not month in r_dict: r_dict[month]= {}
		r_dict[month][week]= df 
	#df_new=DataFrame(dic)
	return( r_dict )

def remove_duplicate_by_index( df ) :
	''' 对name类别有多个重复，则自动的求sum'''
	new_df = DataFrame()
	for i in set(df.index):
		s1 = pd.Series([i] ,index=[ 'name'])
		data_i = df.loc[i]
		if type(data_i) == type(DataFrame()):
			s1 = s1.append(df.loc[i].sum())
		else:
			s1 = s1.append(df.loc[i])
		new_df = new_df.append(s1 , ignore_index=True )
	new_df = new_df.set_index('name')
	return (new_df)

def select_data(all_df , col_names ,row_names ) : 
	'''选择特定的列， 并且根据name进行相应的合并'''
	r_dict = {}
	for month in all_df :
		for week in all_df[month]:
			for a_name in col_names:
				if not a_name in all_df[month][week].columns: 
					print('表头 {0} is not in {1}-{2}'.format(a_name , month , week))
					sys.exit()
			new_df = all_df[month][week].loc[: , col_names+ [row_names]]
			#print(new_df)
			new_df2 = remove_duplicate_by_index(new_df.set_index(row_names))
			if not month in r_dict: r_dict[month]= {}
			r_dict[month][week]= new_df2
			
	return(r_dict)

def get_sum(df_dict ):
	'''针对特定列进行求和'''
	r_dict = {}
	for month in df_dict :
		for week in df_dict[month]:
			s1 = Series(['sum'] ,index=[ 'name'])
			s1 = s1.append(df_dict[month][week].sum())
			#print(s1)
			#print(df_dict[month][week].sum())
			new_df = DataFrame()
			new_df = new_df.append(s1 , ignore_index=True )
			new_df = new_df.set_index('name')
			#print(new_df)
			if not month in r_dict: r_dict[month]= {}
			r_dict[month][week]= new_df
			
	return(r_dict)

def get_ratio(df , new_name , col1 , col2):
	df.insert(df.shape[1] , new_name , df[col1]/df[col2])
	#return new_df

def transformat_data( df_dict , choose_type , col_names = None):
	'''根据month或者week进行数据的返回，x为月/周，值为各列'''
	r_dict = {} 
	if choose_type == 'month':
		for month in sorted(df_dict) :
			s1 = Series(['{0}'.format(month)] , index=['x'])
			if col_names:
				a_df = sum( [ i[col_names] for i in df_dict[month].values()])
			else:
				a_df = sum( [ i for i in df_dict[month].values()])
			for i in a_df.index :
				if not i in r_dict : r_dict[i] = DataFrame()
				s2 = s1.append(a_df.loc[i , col_names]) if col_names else s1.append(a_df.loc[i])
				r_dict[i] = r_dict[i].append(s2 , ignore_index=True )
	elif choose_type == 'week':
		for month in sorted(df_dict) :
			for week in sorted(df_dict[month]):
				s1 = Series(['{0}-{1}'.format(month , week)] , index=['x'])
				a_df = df_dict[month][week]
				for i in a_df.index :
					if not i in r_dict : r_dict[i] = DataFrame()
					s2 = s1.append(a_df.loc(i , col_names)) if col_names else s1.append(a_df.loc[i])
					r_dict[i] = r_dict[i].append(s2 , ignore_index=True )
	else:
		print('error in choose type , month or week')
		exit(1)
	return(r_dict)

def plot_target_items(df_dict , col_name_list, fig_type , fig_title = ''):
	traces=[]
	#print(df_dict)
	#print('bbb')

	if fig_type not in ['bar' , 'line' ] :
		print("你输入的类型暂时不支持，请从以下类型中[bar, line]选择")
		exit(1)
	plot_type = {'bar':go.Bar , 'line':go.Scatter}
	
	tag = '月'; 

	if len( df_dict ) == 1 : 
		for i in df_dict:
			if len( col_name_list ) == 0   : 
				col_names = df_dict[i].columns[1:]
			else:
				col_names = col_name_list
			for j in col_names:
				trace_tmp=plot_type[fig_type]( 
					name=j, 
					x=df_dict[i]['x'],
					y=df_dict[i][j]
				)
				if '-' in df_dict[i]['x'][0]:tag='周'
				traces+=[trace_tmp]
	else:
		for i in df_dict: 
			if len( col_name_list ) == 0   :
				pass
			elif len( col_name_list ) == 1 : 
				trace_tmp=plot_type[fig_type]( 
					name=i, 
					x=df_dict[i]['x'],
					y=df_dict[i][col_name_list[0]])
				if '-' in df_dict[i]['x'][0] : tag='周'
				traces+=[trace_tmp]
			else: 
				for a_name in col_name_list : 
					trace_tmp=plot_type[fig_type]( 
						name=i+'_'+a_name, 
						x=df_dict[i]['x'],
						y=df_dict[i][a_name])
					if '-' in df_dict[i]['x'][0] : tag='周'
					traces+=[trace_tmp]

	#print(trace1)
	if not fig_title :  fig_title="&".join(col_name_list)+tag + "趋势图"  #图形标题

	x_axis_template=dict(
		showgrid=True,  #网格
		zeroline=True,  #是否显示基线,即沿着(0,0)画出x轴和y轴
		nticks=20,
		showline=True,
		title=tag,
		mirror='all'
	)
	
	y_axis_template=dict(
		showgrid=True,  #网格
		zeroline=True,  #是否显示基线,即沿着(0,0)画出x轴和y轴
		nticks=20,
		showline=True,
		title="&".join(col_name_list), #y轴标题
		mirror='all'
	)
	
	layout=go.Layout(
		title=fig_title,
		xaxis=x_axis_template,
		yaxis=y_axis_template
	)
	data=traces
	fig=go.Figure(
		data=data,
		layout=layout
	)
	py.iplot(fig)

def plot( all_dict , data_dict , row_name , type, time_list = ['week', 'month'], all='' , debug = False) :
	#time_list = ['week', 'month']
	type_list = ['line', 'bar']
	if not type in type_list :
		print ( '画图类型请在 [line, bar] 中选择' )
		sys.exit(1)
	col_list = []
	for a_value in data_dict.values() :
		col_list += a_value
	col_list = list(set(col_list))
	#print('aaa')
	new_dict = select_data(all_dict , col_list, row_name )
	if debug : pp.pprint(new_dict)

	if all == 'all' :
		new_dict =get_sum(new_dict)
	for time in time_list : 
		tt = transformat_data( new_dict , time )
		title = []
		for key in data_dict :
			title.append( key )
			if len(data_dict[key]) == 2: 
				[ get_ratio(tt[i] , key , data_dict[key][0] , data_dict[key][1] ) for i in tt ]
		plot_target_items(tt ,title, type)
	#print('ccc')
	
def bar_plot( r_dict, x, title, axis_title_list, barmode=False ) :
	data = []
	for i in r_dict :
		trace = go.Bar( name=i, x=x, y=r_dict[i] )
		data.append( trace )
	x_axis_template=dict(
	showgrid=True,  #网格
	zeroline=True,  #是否显示基线,即沿着(0,0)画出x轴和y轴
	nticks=20,
	showline=True,
	title=axis_title_list[0],
	mirror='all'
	)
		
	y_axis_template=dict(
	showgrid=True,  #网格
	zeroline=True,  #是否显示基线,即沿着(0,0)画出x轴和y轴
	nticks=20,
	showline=True,
	title= axis_title_list[1], #y轴标题
	mirror='all'
	)
	if barmode :
		layout = go.Layout( 
			barmode='stack',
			title = title,
			xaxis=x_axis_template, 
			yaxis=y_axis_template 
		)
	else :
		layout = go.Layout( 
			title = title, 
			xaxis=x_axis_template, 
			yaxis=y_axis_template 
		)
	fig = go.Figure(data=data, layout=layout)
	py.iplot( fig )
	
def multiple_axes_plot( data_dict, x, title, type_dict, title_list ) :
	##### 双纵坐标画图， 柱状图和直线图
	plot_type = {'bar':go.Bar , 'line':go.Scatter}
	yaxis_type = {'bar':'y' , 'line':'y2'}
	data = []
	n = 0
	for i in data_dict :
		n += 1
		fig_type = type_dict[i]
		trace = plot_type[fig_type]( name = i, x = x, y = data_dict[i], yaxis = yaxis_type[fig_type] )
		data.append( trace )
	x_axis_template=dict(
		showgrid=True,  #网格
		zeroline=True,  #是否显示基线,即沿着(0,0)画出x轴和y轴
		nticks=20,
		showline=True,
		title=title_list[0],
		mirror='all'
	)
		
	layout = go.Layout(
		title = title,
		xaxis=x_axis_template ,
		yaxis=dict(
			showgrid=True,  #网格
			zeroline=True,  #是否显示基线,即沿着(0,0)画出x轴和y轴
			nticks=20,
			showline=True,
			title=title_list[1][0],
			mirror='all'
		),
		yaxis2=dict(
			showgrid=True,  #网格
			zeroline=True,  #是否显示基线,即沿着(0,0)画出x轴和y轴
			nticks=20,
			showline=True,
			title=title_list[1][1],
			mirror='all',
			overlaying='y',
			side='right'
		)
	)
	fig = go.Figure(data=data, layout=layout)
	py.iplot(fig)
	
def ratio_calculate( all_dict, col_list, ratio, type_dict, title, yaxis ) : 
	''' 对整体的封装'''
	time_list = ['week', 'month']
	time_dict = { 'week' : '周', 'month': '月' }
	for time in time_list :
		new_dict = select_data(all_dict , col_list, '人员' )
		new_dict = transformat_data( new_dict , time )
		[get_ratio(new_dict[i] , ratio , col_list[0], col_list[1] ) for i in new_dict]
		
		df = new_dict['总体']
		x = df['x'].values.tolist()
		r_dict = {}
		for i in type_dict :
			if not i in r_dict : r_dict[i] = {}
			r_dict[i] = df[i].values.tolist()
		
		title_list = [ time_dict[time], yaxis ]
		multiple_axes_plot( r_dict, x, title, type_dict, title_list )

def stack_bar_plot( all_dict, col_list ) :
	time_list = ['week', 'month']
	new_dict = select_data(all_dict , col_list, '人员' )
	time_dict = { 'week' : '周', 'month': '月' }
	for time in time_list :
		tt = transformat_data( new_dict , time )
		r_dict = {} 
		for key in tt.keys( ) :
			df = tt[key]
			x = df['x'].values.tolist()
			r_dict[key] = df[col_list[0]].values.tolist()
		title_list = [ time_dict[time] , '数目']
		title = '{0}{1}趋势图'.format( col_list[0], time_dict[time] )
		bar_plot( r_dict, x, title, title_list, barmode=True )