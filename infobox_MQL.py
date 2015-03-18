import json
import urllib

import sys

# function to do Search API call
def searchQuery(query):

	api_key = open("api_key.txt").read()
	# print api_key
	# query = 'blue bottle'
	service_url = 'https://www.googleapis.com/freebase/v1/search'
	params = {
	        'query': query,
	        'key': api_key
	}
	url = service_url + '?' + urllib.urlencode(params)
	response = json.loads(urllib.urlopen(url).read())
	return response

# function to do Topic API call
def topicQuery(topic_id):

	api_key = open("api_key.txt").read()
	service_url = 'https://www.googleapis.com/freebase/v1/topic'
	# topic_id = '/m/017nt' # id of bill gates
	params = {
	  'key': api_key,
	  'filter': 'suggest'
	}
	url = service_url + topic_id + '?' + urllib.urlencode(params)
	topic = json.loads(urllib.urlopen(url).read())
	return topic

# Write JSON response to file
def jsonWrite(data, fileName):
	with open(fileName, 'w') as outfile:
		json.dump(data, outfile, sort_keys = True, indent = 4)
	

def main():
	query = sys.argv[1]
	searchResult = searchQuery(query)
	jsonWrite(searchResult, 'search_response.txt')

	print searchResult['result'][0]['mid']

	topicResult = topicQuery(searchResult['result'][0]['mid'])
	# print topicResult['property']
	# for var prop in topicResult:

	# First look into topicResult['property']['/type/object/type']


	jsonWrite(topicResult, 'topic_response.txt')

if __name__ == '__main__':
	main()