from django.shortcuts import render
from django.http import HttpResponse

#import fusion charts library to render charts
from .fusioncharts import FusionCharts

#import pymongo to connect and use the database
from pymongo import MongoClient

from heapq import nlargest

"""
make a connection with MongoDB
"""
client = MongoClient()
db = client.tweetDB						#connect database "tweetDB"
tweets = db.tweet_collection			#connect to collection "twitter_collection"


# views of tweetAnalyzer app


#index view of the webapp
def index(request):
	context = {'name' : "precog"}
	return render(request,'tweetAnalyzer/index.html', context)


#plot distribution of favorite counts and retweets of Original Tweets
def favVsRtCount(request):
	#collect original tweets
	originalTweets = []
	for tweet in tweets.find():
		#insert if tweet is not a retweet itself
		if not( ("retweeted_status" in tweet) or ("RT @" in tweet["text"]) ) :
			originalTweets.append(tweet)
	
	"""
	# restrict the number of original tweets to simulate
	originalTweets = originalTweets[0:min(len(originalTweets),1000)]
	"""

	#count the number of retweets and favorite marks of original tweets
	countDict = {}					#key = "unique id of tweet", value = (favorite count, retweet count)
	for tweet in originalTweets:
		countDict[tweet["id_str"]] = ( tweet["favorite_count"] , tweet["retweet_count"] )

	#prepare the data source
	dataSource = {
				"chart": {
					"caption": "count of Retweet vs favorite",
					"subcaption": "of Original Tweets",
					"yaxisname": "count",
					"xaxisname": "ID of the tweet",
					"paletteColors": "#0075c2,#1aaf5d",
					"captionFontSize": "14",
					"subcaptionFontSize": "14",
					"subcaptionFontBold": "0",
					"showBorder": "0",
					"bgColor": "#ffffff",
					"baseFont": "Helvetica Neue,Arial",
					"showCanvasBorder": "0",
					"showShadow": "1",
					"showAlternateHGridColor": "1",
					"canvasBgColor": "#ffffff",
					"yaxisminValue": "0",
					"forceAxisLimits" : "1",
					"pixelsPerPoint": "0",
					"pixelsPerLabel": "30",
					"lineThickness": "1",
					"compactdatamode" : "1",
					"dataseparator" : "|",
					"labelHeight": "30",				
					"scrollheight": "10",
					"flatScrollBars": "1",
					"scrollShowButtons": "0",
					"scrollColor": "#cccccc",
					"legendBgAlpha": "0",
					"legendBorderAlpha": "0",
					"legendShadow": "0",
					"legendItemFontSize": "10",
					"legendItemFontColor": "#666666"				
				},
				"categories": [{"category":""}],
				"dataset": [
					{"seriesname": "favorite count",
					"data": ""},
					{"seriesname": "retweet count",
					"data": ""}]
			}

	#insert data to data source
	for key, value in countDict.items() :
		dataSource["categories"][0]["category"]+=(key+"|")
		dataSource["dataset"][0]["data"]+=(str(value[0])+"|")
		dataSource["dataset"][1]["data"]+=(str(value[1])+"|")
	#construct the fusionchart
	zoomline = FusionCharts("zoomline", "favVsRtCount", "1300", "500", "chart-container", "json",str(dataSource) )
	#render the chart
	return render(request, 'tweetAnalyzer/favVsRtCount.html', {'output': zoomline.render()})





#show who is more popular ​in the state of Delh​i, Narendra Modi or Arvind Kejriwal
def popularity(request):
	"""
	Metric : the number of tweets with mention of the two persons, 
			i.e. number of tweets related to that person is directly proportional to his popularity
	"""

	#create a dictionary to store tweets corresponding to year of tweets
	tweetYear = {}			#key = "year of tweet", value = "tweet"
	#iterate over all tweets
	for tweet in tweets.find():
		time = tweet["created_at"].split(" ")
		year = time[2]
		#TO-DO: all tweets are in year 2017, so rendering date wise tweets
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
	
	#prepare data for the chart (json)
	dataSource = {"categories":[{"category" : []}],
				"dataset":[{"seriesname" : "Narendra Modi","data" : []},{"seriesname" : "Arvind Kejriwal","data":[]}]}
	#iterate the yearVsPerson dictionary and put data in dataSource
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

	#construct the fusion chart
	lineGraph = FusionCharts("msline", "popularity", "800", "800", "chart-container", "json",str(dataSource) )
	#render the chart
	return render(request, 'tweetAnalyzer/popularity.html', {'output': lineGraph.render()})






#visualise top x hashtags using Pyramid : fusion-charts
def topHashtags(request):
	#how many top hashtags to render 
	topCount = 10	

	#count total hashtags
	totalHashtags = 0
	#create a dictionary to store counts of various hashTags,
	countHashtags = {}				#key = "various hashtags", value = count of that hashtag
	#iterate over all tweets
	for tweet in tweets.find():
		hashtags = tweet["entities"]["hashtags"]
		#iterate over all hashtags in tweet
		for hashtag in hashtags:
			totalHashtags+=1			#increment total hashtag count
			if hashtag["text"] in countHashtags:
				countHashtags[hashtag["text"]]+=1	#increment value in dictionary if key is already present
			else:
				countHashtags[hashtag["text"]] = 1	#create key if not already present
	
	
	#create a heap that would be used to sort out top x hashtags
	heap = []
	for key in countHashtags:
		heap.append((countHashtags[key],key))		#insert a tuple of hashtag and its count in heap
	heap = nlargest(topCount, heap, lambda x: x[0])	#get n largest count hashtags 

	#prepare dataSource
	dataSource = {"data" : []}

	#count of top hashtags that are in top X 
	countTopHashtags = 0

	#put data of top X hashtags and their slice to pyramid
	for top in heap :
		tmpData = top
		countTopHashtags += tmpData[0]
		tmpDict = {"label" : tmpData[1] + str(tmpData[0]),"value" : str(tmpData[0])	}
		dataSource["data"].append(tmpDict)
	
	#TO-DO : other hashtag count is too large compared to top hashtags

	#add a slice for other hashtags
	dataSource["data"].append({"label" : "other hashtags","value" : str(totalHashtags - countTopHashtags)})
	

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
	#render the chart
	return render(request, 'tweetAnalyzer/topHashtags.html', {'output': pyramid.render()})




def tweetGeo(request):
	
	#sample data source
	dataSource = [['Lat','Long','Name'],
			  	[28.5456, 77.2732, 'IIIT Delhi'],
			  	[28.61667, 77.20833, 'Rajya Sabha'],
			  	[28.6144, 77.1996, 'Raj Ghat'],
			  	[28.5933, 77.2507, 'Lotus Temple'],
			  	[28.6562, 77.2410, 'Red fort'],
			  	[28.6129, 77.2295, 'India Gate']]

	"""
	#TO-DO : Twitter API does no longer provide tweet coordinates
	dataSource = [['Lat','Long','Name']]
	for tweet in tweets.find():
		if tweet["coordinates"] == None:
			continue
		tmpData = tweet["coordinates"]["coordinates"].append(tweet["place"]["full_name"])
		dataSource.append(tmpData)
	"""
	
	#render the google chart
	return render(request,'tweetAnalyzer/tweetGeo.html', {	'dataSource' : dataSource})



def tweetTypes(request):
	return HttpResponse("this is not implemented yet")




def tweetVSretweet(request):

	#count the number of retweeted tweets
	countRT = 0					#initialise number of RTweets as 0
	for tweet in tweets.find():
		if ("retweeted_status" in tweet) or ("RT @" in tweet["text"]) :
			countRT+=1

	#number of original tweets
	countOrgT = tweets.find().count() - countRT

	#create the data source json (Dictionary)
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
	#construct the fusion chart , 3D coloumns of original tweet and retweeted tweetsss
	column3d = FusionCharts("column3d", "tweetVSretweet", "400", "650", "chart-container", "json",str(dataSource) )
	#render the chart
	return render(request, 'tweetAnalyzer/tweetVSretweet.html', {'output': column3d.render()})




