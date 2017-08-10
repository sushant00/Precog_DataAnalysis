from django.shortcuts import render
from django.http import HttpResponse

from .fusioncharts import FusionCharts

from pymongo import MongoClient

from heapq import _heapify_max, heappop

"""
make a connection with MongoDB
"""

client = MongoClient()
db = client.tweetDB						#connect database "tweetDB"
tweets = db.tweet_collection			#connect to collection "twitter_collection"


# views of tweetAnalyzer app


def index(request):
	context = {'name' : "precog"}
	return render(request,'tweetAnalyzer/index.html', context)

def tweetLocation(request):

	return HttpResponse("hello vis1")

def topHashtags(request):
	#how many top hashtags to render
	topCount = 10	

	#variable to store total hashtags
	totalHashtags = 0
	#create a dictionary to store counts of hashTags
	countHashtags = {}
	for tweet in tweets.find():
		hashtags = tweet["entities"]["hashtags"]
		for hashtag in hashtags:
			totalHashtags+=1
			if hashtag["text"] in countHashtags:
				countHashtags[hashtag["text"]]+=1
			else:
				countHashtags[hashtag["text"]] = 1
	
	#create a heap that would be used to sort top x hashtags
	heap = []
	for key in countHashtags:
		heap.append((countHashtags[key],key))		#insert a tuple of hashtag and its count in heap
	_heapify_max(heap)									#heapify the tuple list

	#prepare dataSource
	dataSource = {"data" : []}

	#count of top hashtags that are in top X 
	countTopHashtags = 0

	#put data of top X hashtags
	for top in range(topCount) :
		tmpData = heappop(heap)
		countTopHashtags += tmpData[0]
		tmpDict = {"label" : tmpData[1] + str(tmpData[0]),"value" : str(tmpData[0])	}
		dataSource["data"].append(tmpDict)
	"""
	#Warning : other hashtag count is too large compared to top hashtags

	#add a slice for other hashtags
	dataSource["data"].append({"label" : "other hashtags","value" : str(totalHashtags - countTopHashtags)})
	"""

	# prepare the chart
	dataSource["chart"] = {
						"theme": "fint",
						"caption": "Top hashtags",
						"captionOnTop" : "0",
						"captionPadding": "25",
						"alignCaptionWithCanvas" : "1",
						"subcaption": "Credit Suisse 2013",
						"subCaptionFontSize" : "12",
						"borderAlpha": "20",
						"is2D": "0",
						"bgColor": "#ffffff",
						"showValues": "1",
						"numberPrefix": "$",
						"numberSuffix": "M",
						"showPercentValues": "1",
						"chartLeftMargin": "40"
						}
	#prepare the fusionchart
	pyramid = FusionCharts("pyramid","top-hashtags","1400","800","chart-container","json",str(dataSource))
	#render
	return render(request, 'tweetAnalyzer/topHashtags.html', {'output': pyramid.render()})


def tweetVSretweet(request):

	#count the number of retweeted tweets
	countRT = 0					#initialise number of RTweets as 0
	for tweet in tweets.find():
		if (str(tweet["retweeted"])=="true") or ("RT @" in tweet["text"]) :
			countRT+=1
	#number of original tweets
	countOrgT = tweets.find().count() - countRT
	dataSource = {"chart": {
					"caption": "Distribution of Original Tweets vs ReTweets",
					"subCaption": "tweets related to Arvind Kejriwal and PM Modi",
					"xAxisName": "Type of Tweets",
					"yAxisName": "Number of Tweets",
					"paletteColors": "#0075c2",
					"valueFontColor": "#ffffff",
					"baseFont": "Helvetica Neue,Arial",
					"captionFontSize": "15",
					"subcaptionFontSize": "15",
					"subcaptionFontBold": "0",
					"placeValuesInside": "1",
					"rotateValues": "1",
					"showShadow": "1",
					"divlineColor": "#999999",			   
					"divLineIsDashed": "1",
					"divlineThickness": "1",
					"divLineDashLen": "1",
					"divLineGapLen": "1",
					"canvasBgColor": "#ffffff"
				},
			"data": [{
						"label": "Original Tweets",
						"value": str(countOrgT)
					},
					{
						"label": "Retweets",
						"value": str(countRT)
					}]
			}
	column3d = FusionCharts("column3d", "tweetVSretweet", "400", "650", "chart-container", "json",str(dataSource) )
	return render(request, 'tweetAnalyzer/tweetVSretweet.html', {'output': column3d.render()})

def tweetTypes(request):
	return HttpResponse("hello vis4")