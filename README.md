# Tweet Analyzer
django based web-application to visualise the tweets using fusion charts and google-charts, curated from Twitter API, collected in MongoDB 



# Quick Start

## Installation:

### Applications
	-install python 3.x
	-install django 1.11 or above (stable release)
	-mongoDB 3.x

### Libraries for python
	-twitter 1.17.x or above : 
		Windows  : python -m pip install twitter

	-pymongo :
		Windows  : python -m pip install pymongo

### Now Follow these Steps:
	1. download the django project
	2. open command prompt
    type : mongod --dbpath "<full path to mongodb directory in data_Analyzer directory>"
    e.g. mongod --dbpath "C:\Downloads\data_Analyzer\mongodb"

	3. open new command prompt (do not close the previous one)
	  change directory to downloaded project "data_Analyzer" 
	  type : python3 manage.py runserver
	4. visit url "127.0.0.1:8000/tweetAnalyzer"
