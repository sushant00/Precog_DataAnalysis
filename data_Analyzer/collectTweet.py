from pymongo import ASCENDING, MongoClient

from twython import Twython
"""
twitter OAuth,
enter the auth details to access TwitterAPI
on behalf of that UserAccount

ACCESS_TOKEN = ""
ACCESS_TOKEN_SECRET = ""
CONSUMER_KEY = ""
CONSUMER_SECRET = ""

"""



twitterAPI = Twython(app_key = CONSUMER_KEY,
					app_secret = CONSUMER_SECRET,
					oauth_token = ACCESS_TOKEN,
					oauth_token_secret = ACCESS_TOKEN_SECRET)
"""
make a connection with MongoDB
"""

client = MongoClient()
db = client.tweetDB						#create/connect database "tweetDB"
#db.tweet_collection.drop()				#delete the previously stored collection, if exists
tweets = db.tweet_collection			#connect to collection "twitter_collection"


#create index on (id and timestamp) of tweets
tweets.create_index([('id',ASCENDING), ('timestamp_ms',ASCENDING)],unique = True)


"""
set variables for querying Twitter REST API
"""	
#number of tweets to collect
count = 100	
#keywords of which data is collected
hashtags = ["pmoindia","delhicm","arvindkejriwal"]
# "narendra modi","arvind kejriwal","narendramodi"895873408327499776

# query and fetch data
for hashtag in hashtags:
	response = twitterAPI.search(q = hashtag, count = count)
	statuses = response["statuses"]
	print(len(statuses))
	for status in statuses:
		try:
			tweets.insert(status)
		except:
			pass

print("Success")
print(tweets.find().count(),"tweets collected")

while tweets.find().count() < 10000:
	print("check")

	for hashtag in hashtags:
		response = twitterAPI.search(q = hashtag, count = count, max_id = "891893408327499776" )
		statuses = response["statuses"]
		print(len(statuses))
		for status in statuses:		
			try:
				tweets.insert(status)
			except:
				pass
	print("Success")
	print(tweets.find().count(),"tweets collected")
