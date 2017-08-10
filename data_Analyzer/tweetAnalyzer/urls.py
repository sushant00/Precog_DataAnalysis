from django.conf.urls import url

from . import views

app_name = 'tweetAnalyzer'
urlpatterns = [
	url(r'^$', views.chart, name='index'),
	url(r'^tweetLocation$', views.tweetLocation, name='tweetLocation'),
	url(r'^topHashtags$', views.topHashtags, name='topHashtags'),
	url(r'^tweetVSretweet$', views.tweetVSretweet, name='tweetVSretweet'),
	url(r'^tweetTypes$', views.tweetTypes, name='tweetTypes'),
]