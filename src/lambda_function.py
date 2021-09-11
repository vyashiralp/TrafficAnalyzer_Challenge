#import modin.pandas as pd
#from modin.utils import to_pandas
import pandas as pd
import urllib.parse as urlparse 
from urllib.parse import parse_qs
import numpy as np
import boto3
import s3fs
from datetime import date
import os
import json

class TrafficAnalyser(object):
	"""
	INPUTS:
		- filepath: location of file in <s3??>
			- Type: String

		- long_report: (optional) Flag to generate long report for detailed analysis.
			- Type: Bool | Default: True

	OUTPUTS:

	METHODS:
		- 

	"""
	def __init__(self, filepath, long_report = False):
		self.filepath = filepath
		self.long_report_flag = long_report

		# MISC CONFIG
		self.long_report_columns = ['ip', 'referrer_host', 'potential_search_term', 'category', 'product_name', 'number_of_items', 'total_revenue']


	def preprocess_product_list(self,df):
		"""
		INPUT: 
			- Dataframe : dataframe obtained from reading the tsv file
		"""
		try:
		  df = df.copy()
		  # Fill missing product_lists
		  df['product_list'] = df['product_list'].fillna(';'*5)

		  # If multiple products are involved, split them in seperate rows
		  df['product_list'] = df['product_list'].str.split(',')
		  df = df.explode('product_list')

		  # Split product_list details
		  df['product_list'] = df['product_list'].str.split(';')
		  df['product_list_len'] = df['product_list'].str.len()

		  # Mitigate missing merchandizing_evar
		  df['product_list'] = df['product_list'].apply(lambda x: [*x, *['']*(6-len(x))] if len(x) < 6 else x)
		  df['product_list_len'] = df['product_list'].str.len()

		  # Parse product list and merge with main df
		  product_list_explode_columns = ['category', 'product_name', 'number_of_items', 'total_revenue', 'custom_events', 'merchandizing_eVar']

		  product_list_explode_df = pd.DataFrame(df.product_list.tolist(), index = df.index)
		  product_list_explode_df.columns = product_list_explode_columns
		  df = pd.merge(df, product_list_explode_df, right_index=True, left_index=True)
		except:
			raise ValueError('Length Mismatch')
		return df
		

	def get_revenue_search_engine_keyword(self,df):
	  groupby_columns = ['ip']
	  df.sort_values('date_time', inplace = True)
	  # Convert to pandas 
	  pandas_df=  pd.DataFrame(df)
	  # Get revenue and referrer info for each session in one dataframe
	  revenue_df = pandas_df.groupby(groupby_columns).apply(lambda grp: self.get_revenue(grp)).reset_index()
	  referrer_df = pandas_df.groupby(groupby_columns).apply(lambda grp: self.get_search_engine_keyword(grp)).reset_index()
	
	  op_df = referrer_df.merge(revenue_df, on=groupby_columns, how = 'left') # Left merge because we can have search terms which have no revenue. 
	                                                               # Business might be interested in these trends

	  op_df['total_revenue'] = pd.to_numeric(op_df['total_revenue']).fillna(0).astype(int)

	  print(op_df)
	  
	  return pd.DataFrame(op_df)


	def generate_summary_report(self, df):
		"""
		"""
		return df.groupby(['referrer_host', 'potential_search_term']).agg({'total_revenue':'sum'}).reset_index().sort_values(by= 'total_revenue',ascending=False)

	def generate_long_report(self, df):
		"""
		"""
		return df[[self.long_report_columns]]


	def get_search_term(self,url):
		"""
		Try extracting search term from each URL

		"""
		search_term_keys = ('q','p','k')  #This list will have to evolve over time to improve accuracy of discovering keywords

		keyword_list= []
		query_string = urlparse.urlparse(url) 

		for param, value in parse_qs(query_string.query).items():
		  if param in search_term_keys:
			  keyword_list.append(value[0].lower())

		if len(keyword_list) < 1:
			return np.NaN
		return keyword_list[0]

	def get_search_engine(self,url):
		"""
		Get the referrer domain
		"""
		search_engine_list = []
		query_string = urlparse.urlparse(url) 
		search_engine_list.append(query_string.netloc)

		if len(search_engine_list) < 1:
			return np.NaN
		return search_engine_list[0]


	def get_revenue(self,df):
		output_columns = ['geo_city', 'geo_region', 'geo_country', 'category', 'product_name', 'number_of_items', 'total_revenue']
		if 1 in df.event_list:
			return df[df.event_list == 1][output_columns]
		else:
			return "Event list is not 1"

	def get_search_engine_keyword(self,df):
		df.sort_values('date_time', inplace = True)

		keywords = df['potential_search_term'].unique()
		hosts = df['referrer_host'].unique()

		return df[~df.potential_search_term.isna()][['potential_search_term', 'referrer_host']].iloc[0]

	def process_file(self):
		"""
		"""
		df = pd.read_csv("s3://website-traffic-artifacts/"+self.filepath,delimiter = '\t')
		processed_df = self.preprocess_product_list(df)
		print(processed_df.head())
		processed_df['potential_search_term'] = processed_df['referrer'].apply(lambda x: self.get_search_term(str(x)))
		processed_df['referrer_host'] = processed_df['referrer'].apply(lambda x: self.get_search_engine(str(x)))
		dilated_df = self.get_revenue_search_engine_keyword(processed_df)

		if self.long_report_flag:
			output_df = self.generate_long_report(dilated_df)
		else:
			output_df = self.generate_summary_report(dilated_df)

		return output_df

def check_file_exist_s3(client, bucket, key):
    """return the key's size if it exist, else None"""
    prefix = "output"
    key = 'output/' + key
    response = client.list_objects_v2(
        Bucket=bucket,
        Prefix=prefix,
    )
    for obj in response.get('Contents', []):
    	if obj['Key'] == key:
        	print("Exists")
        	return obj['Size']
			
def send_email(exec_date,bucketname,filename,output_filename):
	s3_client = boto3.client("s3",region_name= 'us-west-2')
	file_size = check_file_exist_s3(s3_client,bucketname,output_filename)
	client = boto3.client('sns')
	sns_arn = os.environ['wa_sns_topic_arn']
	if file_size > 0 :
		
		response = client.publish (
		  TargetArn = sns_arn,
		  Message = json.dumps({'default': "File Successfully created and uploaded at url: s3://website-traffic-artifacts/output/"+str(exec_date)+'_SearchKeywordPerformance.tab.tsv'}),
		  MessageStructure = 'json'
	   )
	else:
		response = client.publish (
		  TargetArn = sns_arn,
		  Message = json.dumps({'default': "File Successfully created but with size 0"}),
		  MessageStructure = 'json'
	   )
		
		
def lambda_handler(event, context):

	filename = event['Records'][0]['s3']['object']['key']
	bucketname= event['Records'][0]['s3']['bucket']['name']
	tf = TrafficAnalyser(filename)
	result = tf.process_file()
	exec_date= date.today()
	result.columns = ['Search Engine Domain','Search Keywords','Revenue']
	output_filename = str(exec_date)+'_SearchKeywordPerformance.tab.tsv'
	result.to_csv("s3://"+bucketname+"/output/"+output_filename,sep ='\t', index=False)
	send_email(exec_date,bucketname,filename,output_filename)
	
		
	

