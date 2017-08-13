from django.conf.urls import url

from . import views

app_name = 'tweetAnalyzer'
urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^favVsRtCount$', views.favVsRtCount, name='favVsRtCount'),
	url(r'^popularity$', views.popularity, name='popularity'),
	url(r'^topHashtags$', views.topHashtags, name='topHashtags'),
	url(r'^tweetGeo$', views.tweetGeo, name='tweetGeo'),
	url(r'^tweetTypes$', views.tweetTypes, name='tweetTypes'),
	url(r'^tweetVSretweet$', views.tweetVSretweet, name='tweetVSretweet'),
]