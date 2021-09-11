# TrafficAnalyzer_Challenge


Input : Hit Level Data 


Output: 
- Search Engine Domain (i.e. google.com) 
- Search Keyword (i.e. "Laffy Taffy") 
- Revenue (i.e. $12.95)

**data folder** : Consists of input data files and data test files

**deployment folder** : This folder holds terraform scripts for building AWS resources like lambda, s3, sns ,roles and policies

**src folder**: This folder holds python script to answer business question :
##### How much revenue is the client getting from external Search Engines, such as Google, Yahoo and MSN, and which keywords are performing the best based on revenue?
       Also hold test file which consists of 2 unit test cases 
       1. unit test 1 checks if function raises a value error when extra columns are passed for product_list
       2. unit test 2 checks if get_revenue function goes to else when event_list 1 is not found
     
**documents folder** : 1. Folder consists of a word file while hold high level technical architecture and details for the project
                2. Also contains a PPT to get a view of the Business Problem and the approch taken.
            
            



