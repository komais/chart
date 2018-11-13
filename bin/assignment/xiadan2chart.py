#! /usr/bin/env python3
import argparse
import sys
import os
import re
import pandas as pd
import pandas
import numpy as np
import sys
from pandas import Series,DataFrame #此两个为pandas中的数据结构，特别是DataFrame 非常实用
import glob,os
import pprint as pp


__author__='Liu Tao'
__mail__= 'taoliu@annoroad.com'
'''条目的增减，人员增减'''

class project():
	def __init__(self , content_list):
		self.week   = content_list[0]
		content = content_list[1]
		
		self.group_name  = content[0]
		self.id     = content[1]
		self.person = content[3]
		self.need_report = str(content[7])
		self.project_type = content[8]
		self.source = content[11]
		self.time = content[12]
		self.status = str(content[15])
		self.finish_report = str(content[17])


def get_files(pathway , week):
	''' 输入是一个路径，下面包含xlsx， 返回第一个excel的指定的sheet的titile'''
	all_files = glob.glob("{0}/*{1}.xlsx".format(pathway, week))  #文件存储路径
	if len(all_files) == 0 :
		sys.exit('file is not exists in {0}'.format(pathway))
	else:
		return( all_files )

def read_xlsx(file1 , week , sheet_index=0 , index_col=1 ):
	''' 读取所有文件指定的sheet，返回一个大的dataframe'''
	df=pd.read_excel(file1,sheet_name= sheet_index )
	df=df.fillna(0)
	df = df.set_index(df.columns[ index_col ])
	if week in df.index:
		this_week_df = df.loc[week , :]
		if isinstance(this_week_df , pandas.core.series.Series):
			this_week_df = pd.DataFrame(this_week_df).T
		before_index = df.index.unique().get_loc( week )
		before_week_df = df.loc[ df.index.unique()[:before_index], : ]
		return( this_week_df, before_week_df , True)
	else:
		return False,False ,False


def init_dict(a_list , r_dict ):
	index_list = ['组别' , '周次' , '总下单数','完成下单数', '应交高质量报告数',
	'提交高质量报告数','延期项目数','暂停项目数','内部沟通','市场支持','出差','禅道bug']
	for a_project in a_list:
		#print(a_project.person)
		if not a_project.person in r_dict:
			r_dict[a_project.person] = pd.Series(0 , index= index_list)
		r_dict[a_project.person].loc['组别'] = a_project.group_name 
		r_dict[a_project.person].loc['周次'] = a_project.week 
		
	return(r_dict)
	
def get_number_for_this_week(r_dict , a_list):
	for a_project in a_list :
		a_item = r_dict[ a_project.person ]
		a_item.loc['总下单数'] += 1 
		if '完成' in a_project.status : a_item.loc['完成下单数'] += 1 
		if '延期' in a_project.status : a_item.loc['延期项目数'] += 1 
		if '暂停' in a_project.status : a_item.loc['暂停项目数'] += 1 
		if '是' in a_project.need_report : a_item.loc['应交高质量报告数'] += 1 
		if '是' in a_project.finish_report : a_item.loc['提交高质量报告数'] += 1 

def get_number_for_last_week(r_dict , a_list):
	for a_project in a_list :
		if a_project.person not in r_dict : continue
		a_item = r_dict[ a_project.person ]
		if '延期' in a_project.status : a_item.loc['延期项目数'] += 1 

def add_other_job(r_dict, a_df):
	for i in a_df.iterrows():
		print(i[1][0])
		job_type = i[1][0]  ## 由于week做了index，少了一列，编号都提前
		if job_type not in ['内部沟通','市场支持','出差','禅道bug'] :  continue
		job_dutyer = i[1][5].split('、')
		for a_people in job_dutyer:
			if a_people in r_dict:
				r_dict[a_people].loc[job_type] += 1 

def main():
	parser=argparse.ArgumentParser(description=__doc__,
			formatter_class=argparse.RawDescriptionHelpFormatter,
			epilog='author:\t{0}\nmail:\t{1}'.format(__author__,__mail__))
	parser.add_argument('-p','--pathway',help='pathway',dest='pathway',required=True)
	parser.add_argument('-fw','--fweek',help='file week name',dest='fweek',required=True)
	parser.add_argument('-w','--week',help='week name',dest='week',required=True)
	parser.add_argument('-o','--output',help='output file',dest='output',required=True)
	parser.add_argument('-e','--ee',help='extract job file',dest='ee',action='store_true')
	args=parser.parse_args()

	file_pathway = get_files(args.pathway, args.fweek)
	result_dict = {}
	if args.ee:
		pd_list = []
		for a_file in file_pathway:
			print(a_file,args.week)
			new_df , old_df , flag = read_xlsx( a_file , args.week , 0 ) 
			#print(new_df)
			if flag : pd_list.append(new_df)
		new_df = pd.concat(pd_list, axis=0 , sort=False, join='outer')
		with pd.ExcelWriter(args.output , engine='openpyxl') as writer:
			new_df.to_excel(writer, sheet_name='Sheet1')
	else : 
		for a_file in file_pathway:
			#print(a_file)
			new_df , old_df , flag = read_xlsx( a_file , args.week , 0 ) 
			#pp.pprint(new_df)
			#pp.pprint(old_df)
			if flag : 
				new_list = [ project(i) for i in new_df.iterrows() ]
				old_list = [ project(i) for i in old_df.iterrows() ]
				result_dict = init_dict( new_list ,result_dict ) 
			#pp.pprint(result_dict)
				get_number_for_this_week( result_dict , new_list) 
				get_number_for_last_week( result_dict , old_list)
			
			new_df2 , old_df2 ,flag= read_xlsx( a_file , args.week , 1, index_col=0 )
			if flag : 
				#pp.pprint(new_df2)
				add_other_job(result_dict , new_df2)

			
			result_df = pd.DataFrame( result_dict )
		with pd.ExcelWriter(args.output) as writer:
			result_df.T.to_excel(writer, sheet_name='Sheet1')


if __name__ == '__main__':
	main()


