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
	elif "周次" in df.columns:
		date=list(set(list(df["周次"])))
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
	''' 读取所有文件指定的sheet，返回一个大的dataframe'''
	pd_list = []
	for f in all_files:
		df=pd.read_excel(f,sheet_name= sheet_index ) #默认读取表格第一个sheet，如果想跟换为第二个sheet，可以更改为：sheet_name=1
		df=df.fillna(0)
		name=os.path.split(f)[1]
		month , week =get_date(name,df)
		df['month']= month
		#print (date)
		pd_list.append( df )
	r_df = pd.concat(pd_list, axis=0 , sort=False, join='outer')
	#df_new=DataFrame(dic)
	return( r_df )

def upgrade_df(df , a_list):
	'''给dataframe添加特定的列，例如
	upgrade_df(all_df1, [ ['完成项目总数',['完成商业项目数','完成个性化数'],'+'] ,
	['在线项目总数',['下机项目数','接入个性化数'],'/']])  '''
	for result , a  ,symbol in a_list : 
		if result in df.columns:
			bool_list = df[ result ].isna()
			if symbol == '+' : 
				tt = 0
				flag = False
				for i in a :
					if flag  : 
						tt += df[i][bool_list]
					else:
						tt = df[i][bool_list]
						flag = True
				df[result][bool_list] = tt
			elif symbol == '/':
				df[result][bool_list]  = df[a[0]][bool_list]  / df[a[1]][bool_list]
			elif symbol == '-' : 
				df[result][bool_list]  = df[a[0]][bool_list]  - df[a[1]][bool_list]
			elif symbol == '*' : 
				df[result][bool_list]  = df[a[0]][bool_list]  * df[a[1]][bool_list]
			else:
				sys.exit('{0} is error'.format(symbol))
		else:
			if symbol == '+' :
				df[result] = df[a].sum(axis=1)
			elif symbol == '/':
				df[result] = df[a[0]] / df[a[1]]
			elif symbol == '-':
				df[result] = df[a[0]] - df[a[1]]
			elif symbol == '*':
				df[result] = df[a].product(axis=1)
			else:
				sys.exit('{0} is error'.format(symbol))

def add_week(df , key , start = 0 ):
	def date2week(tt):
		year, month , day =tt.year , tt.month, tt.day
		calendar.setfirstweekday(start)
		x= np.array(calendar.monthcalendar(year, month))
		if x[0][0] == 0:
			week_number = np.where(x ==day)[0][0] -1 
		else:
			week_number = np.where(x ==day)[0][0]
		if week_number == -1 : 
			if month == 1 : 
				y = np.array(calendar.monthcalendar(year-1, 12))
				if y[0][0] == 0 :
					tt = y.shape[0] - 1 
				else:
					tt = y.shape[0]
				return('{0}月{1}周'.format('12' , tt))
            #return('{0}月{1}周'.format('12' , tt+1))
			else: 
				y = np.array(calendar.monthcalendar(year, month-1))
				if y[0][0] == 0 :
					tt = y.shape[0] - 1 
				else:
					tt = y.shape[0]
				return('{0}月{1}周'.format(month-1 , tt))
            #return('{0}月{1}周'.format(month-1 , tt+1))
		else:
			return ('{0}月{1}周'.format(month , week_number+1))
	df['week_number'] = list(map(date2week , df[key]))

def sort_by_index(df):
	tt = lambda x:int(x.replace('月','').replace('周','').replace('-',''))
	if type(df.index) == pd.MultiIndex:
		df['seq'] = list(map(tt , df.index.get_level_values(0)))
	else:
		df['seq'] = list(map(tt , df.index))
	df = df.sort_values(by='seq').drop(['seq'],axis=1)
	return df

def retype(df,key,function):
	df[key] = list(map(function , df[key]))

class myPlot():
	def __init__(self, df ) :
		''' 以index为x轴，column name为y轴进行绘图，数据转换有fromat完成'''
		self.df = df

	
	def plot(self , fig_type , tag='周' , fig_title=None):
		df =self.df
		#x = self.x
		y = set(df.columns.get_level_values(0))
		if fig_type not in ['bar' , 'line','stack_bar' ] :
			print("你输入的类型暂时不支持，请从以下类型中[bar, line]选择")
			sys.exit(1)
		plot_type = {'bar':go.Bar , 'line':go.Scatter , 'stack_bar':go.Bar}
	
		traces = []
		dash_type = ["solid", "dot", "dash", "longdash", "dashdot", "longdashdot"] * 10
		if type(df.columns) == pd.MultiIndex:
			for j in y:
				for i,m in enumerate(set(df.columns.get_level_values(1))):
					#print(j,m,"dddddddddd")
					if fig_type == 'line':
						trace_tmp=plot_type[fig_type]( 
							name="{0}({1})".format(j,m), 
							x=df.index,
							y=df[j,m],
							line = dict(dash = dash_type[i])
						)
					else:
						trace_tmp=plot_type[fig_type]( 
							name="{0}({1})".format(j,m), 
							x=df.index,
							y=df[j,m]
						)
					traces+=[trace_tmp]
		else:
			for j in y: 
				#print(df.index)

				trace_tmp=plot_type[fig_type]( 
					name=j, 
					x=df.index,
					y=df[j]
					)
				#print(df.index)
				traces+=[trace_tmp]
		if not fig_title :  fig_title="&".join(y)+tag + "趋势图"  #图形标题
		x_axis_template=dict(
			showgrid=True,  #网格
			zeroline=True,  #是否显示基线,即沿着(0,0)画出x轴和y轴
			nticks=20,
			showline=True,
			title=tag,
			mirror='all',
			type="category",
		)
		
		y_axis_template=dict(
			showgrid=True,  #网格
			zeroline=True,  #是否显示基线,即沿着(0,0)画出x轴和y轴
			nticks=20,
			showline=True,
			title="&".join(y), #y轴标题
			mirror='all'
		)
		
		if fig_type=='stack_bar':
			layout=go.Layout(
				barmode='stack',
				title=fig_title,
				xaxis=x_axis_template,
				yaxis=y_axis_template
			)
		else:
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
		py.iplot(fig )

class format():
	def __init__(self, df, x ,y ):
		self.raw_df = df 
		self.x  = x
		self.y  = y
		select_list = [x] + y
		self.df = self.raw_df[select_list]
		self.average_col = None 
		self.group_col = None 
	def get_total_ratio(self , new_colname , extract=[] ):
		'''sum then get ratio'''
		if self.group_col:
			self.df = self.df.groupby( [self.x ,self.group_col ]).sum()
		else:
			self.df = self.df.groupby( self.x ).sum()
		col_list = []
		#print(new_colname)
		for i in new_colname:
			#print(i)
			new_col, col1 , col2 , symbol = i 
			if symbol == '/' : 
				self.df[ new_col ] = self.df[ col1 ] / self.df[ col2 ] 
			else:
				sys.exit('{0} is error'.format(symbol))
			col_list.append(new_col)
		return(self.extract_column(col_list + extract))
	def judge_and_replace(self , key , value , method =None, new_key=None):
		if not new_key:
			new_key = '{0}_bool'.format(key)
		if method :
			self.df[new_key] = getattr(self.df[key] , method) > value
		else:
			self.df[new_key] = self.df[key] > value
	def select_by_value(self , key ,value):
		self.df = self.df[self.df[key] == value]
	def extract_column(self, col_list):
		if self.group_col:
			return pd.DataFrame(self.df[col_list]).unstack()
		else:
			return pd.DataFrame(self.df[col_list])
	def get_average_by(self , colname):
		self.df = pd.concat([self.df , self.raw_df[colname]] , axis=1)
		self.average_col = colname 
	def add_group(self , colname):
		self.df = pd.concat([self.df , self.raw_df[colname]] , axis=1)
		self.group_col = colname
	def groupby(self , stat_type):
		r_df = ''
		if stat_type == 'count': 
			if self.group_col and not self.average_col: 
				r_df = self.df.groupby([self.x , self.group_col]).count().unstack()
			elif self.average_col and not self.group_col :
				r_df = self.df.groupby([self.x , self.average_col]).count()
				r_df = r_df.groupby(self.x).mean()
			elif self.average_col and  self.group_col :
				r_df = self.df.groupby([self.x , self.group_col, self.average_col]).count()
				r_df = r_df.groupby([self.x ,self.group_col] ).mean().unstack()
			else:
				r_df = self.df.groupby(self.x).count()
		elif stat_type == 'sum':
			if self.group_col and not self.average_col: 
				r_df = self.df.groupby([self.x , self.group_col]).sum().unstack()#.unstack() ##2.1.3 in analysisi
				#print(r_df.index)
			elif self.average_col and not self.group_col :
				r_df = self.df.groupby([self.x , self.average_col]).sum().groupby(self.x).mean()
			elif self.average_col and  self.group_col :
				r_df = self.df.groupby([self.x , self.group_col, self.average_col]).sum()
				r_df = r_df.groupby([self.x ,self.group_col] ).mean().unstack()
			else:
				r_df = self.df.groupby(self.x).sum()
		elif stat_type == 'mean':
			if self.group_col and not self.average_col: 
				r_df = self.df.groupby([self.x , self.group_col]).mean().unstack()
			elif self.average_col and not self.group_col :
				r_df = self.df.groupby([self.x , self.average_col]).mean().groupby(self.x).mean()
			elif self.average_col and  self.group_col :
				r_df = self.df.groupby([self.x , self.group_col, self.average_col]).mean()
				r_df = r_df.groupby([self.x ,self.group_col] ).mean().unstack()
			else:
				r_df = self.df.groupby(self.x).mean()
		else:
			sys.exit('{0} is error'.format(stat_type))
		#print('mmm')
		return (r_df)


def get_rank(df , index_col , colname , used_date = None , quantile=0.8, compare='>' , used_column='日期（格式“月-周次”）' , exclude = [] ,sort_index=False):
	if len(exclude) > 0 : df.drop(exclude)

	if used_date : 
		ss = df[[index_col,colname, used_column ]].groupby([used_column,index_col]).sum()
		if sort_index : ss=sort_by_index(ss)
		a_df = ss.loc[ss.index.get_level_values(0).unique()[-used_date:],].groupby(index_col).sum()
	else: 
		a_df = df[[index_col , colname]].groupby(index_col).sum()
	#print (a_df)
	value = float(a_df.quantile( quantile ))
	if compare == '>':
		bool_list = a_df[colname] >=  value
		r_df = a_df.loc[a_df.index[bool_list],].sort_values(colname , ascending=False)
	elif compare == '<':
		bool_list = a_df[colname] <= value
		r_df = a_df.loc[a_df.index[bool_list],].sort_values(colname )
	return (r_df)

def get_trend(df, index_col , value_col , used_date = None ,quantile=0.8, compare='>' , trend = False , used_column='日期（格式“月-周次”）' , exclude=[] , sort_index=False): 
	increasing = lambda L: all(x<=y for x, y in zip(L, L[1:]))
	decreasing = lambda L: all(x>=y for x, y in zip(L, L[1:]))

	if len(exclude) > 0 : df.drop(exclude)

	tt = df[[index_col,used_column, value_col]]
	ss = tt.pivot(index= index_col ,columns=used_column, values=value_col)
	if sort_index :  ss=sort_by_index(ss.T).T
	if used_date:
		ss = ss.loc[: , ss.columns[-used_date:]]
	if compare == '>':
		pp = ss >= ss.quantile(quantile)
		r_df = ss.loc[pp.all(1),]
		if trend : 
			r_df =r_df[r_df.apply(increasing , axis =1 )]
	elif compare == '<' :
		pp = ss <= ss.quantile(quantile)
		r_df = ss.loc[pp.all(1),]
		if trend : 
			r_df =r_df[r_df.apply(decreasing , axis =1 )]
	return(r_df)
