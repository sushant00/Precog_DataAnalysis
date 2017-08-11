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
	
	#sample data source
	dataSource = [['Lat','Long','Name'],[37.4232, -122.0853, 'Work'],
		  [37.4289, -122.1697, 'University'],
		  [37.6153, -122.3900, 'Airport'],
		  [37.4422, -122.1731, 'Shopping']]

	"""
	#dataSource = [['Lat','Long','Name']]
	for tweet in tweets.find():
		if tweet["coordinates"] == None:
			continue
		tmpData = tweet["coordinates"]["coordinates"].append(tweet["place"]["full_name"])
		dataSource.append(tmpData)"""
	return render(request,'tweetAnalyzer/tweetLocation.html', {	'dataSource' : dataSource})

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
	pyramid = FusionCharts("pyramid","top-hashtags","1200","800","chart-container","json",str(dataSource))
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


def popularity(request):

	#create a dictionary to store tweets corresponding to year of tweets
	tweetYear = {}
	for tweet in tweets.find():
		time = tweet["created_at"].split(" ")
		year = time[2]
		if year in tweetYear:
			tweetYear[year].append(tweet)
		else:
			tweetYear[year] = [tweet]

	#create a dictionary to store count of tweets with mention of narendra modi/arvind kejriwal in that year
	yearVsPerson = {}

	for year in tweetYear:
		countModi = 0
		countArvind = 0
		for tweet in tweetYear[year]:
			if "narendra modi" in tweet["text"] or "narendramodi" in tweet["text"] or "pmo india" in tweet["text"]:
				countModi +=1
			if "arvind kejriwal" in tweet["text"] or "arvindkejriwal" in tweet["text"] or "cmo delhi" in tweet["text"] or "cmodelhi" in tweet["text"]:
				countArvind+=1
		yearVsPerson[year] = (countModi, countArvind)			
	
	dataSource = {"categories":[{"category" : []}],
				"dataset":[{"seriesname" : "Narendra Modi","data" : []},{"seriesname" : "Arvind Kejriwal","data":[]}]}
	for key in yearVsPerson:
		dataSource["categories"][0]["category"].append({"label" : key})
		dataSource["dataset"][0]["data"].append({"value":yearVsPerson[key][0]})
		dataSource["dataset"][1]["data"].append({"value":yearVsPerson[key][1]})

	#add chart properties
	dataSource["chart"] = {
			"caption": "popularity of Narendra Modi vs Arvind Kejriwal",
			"linethickness": "2",
			"showvalues": "0",
			"formatnumberscale": "1",
			"labeldisplay": "ROTATE",
			"slantlabels": "1",
			"divLineAlpha": "40",
			"anchoralpha": "0",
			"animation": "1",
			"legendborderalpha": "20",
			"drawCrossLine": "1",
			"crossLineColor": "#0d0d0d",
			"crossLineAlpha": "100",
			"tooltipGrayOutColor": "#80bfff",
			"theme": "zune"
		}

	lineGraph = FusionCharts("msline", "popularity", "800", "800", "chart-container", "json",str(dataSource) )
	return render(request, 'tweetAnalyzer/popularity.html', {'output': lineGraph.render()})
