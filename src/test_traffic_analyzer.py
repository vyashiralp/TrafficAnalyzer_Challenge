import unittest
import pandas as pd

from lambda_function import TrafficAnalyser

class TestTrafficAnalyzerMethods(unittest.TestCase):
	

	def test_errors_raised(self):
		test_data_file = '../data/input/data_test_file.tsv'
		tdf = pd.read_csv(test_data_file, delimiter = '\t')
		tdf.sort_values('ip', inplace = True)
		with self.assertRaises(ValueError):
			TrafficAnalyser.preprocess_product_list(self,tdf)
			
	def test_event_list(self):
		df_test = pd.DataFrame(['1254033478','9/27/2009 6:37','Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_4_11; en) AppleWebKit/525.27.1 (KHTML, like Gecko) Version/3.2.1 Safari/525.27.1',
		'112.33.98.231',2,'Salt Lake City','UT','US','Home','http://www.esshopzilla.com','Electronics;Zune - 328GB;1;;'
		,'http://search.yahoo.com/search?p=cd+player&toggle=1&cop=mss&ei=UTF-8&fr=yfp-t-701','Electronics','Zune','1',0])
		df_test.index =['hit_time_gmt','date_time','user_agent','ip','event_list','geo_city','geo_region','geo_country','pagename','page_url','product_list','referrer','category','product_name', 'number_of_items', 'total_revenue']

		self.assertEqual(TrafficAnalyser.get_revenue(self,df_test.T),'Event list is not 1')
		
            
if __name__=='__main__':
    unittest.main()