import json
import urllib

def searchQuery():

	api_key = open("api_key.txt").read()
	print api_key
	query = 'blue bottle'
	service_url = 'https://www.googleapis.com/freebase/v1/search'
	params = {
	        'query': query,
	        'key': api_key
	}
	url = service_url + '?' + urllib.urlencode(params)
	response = json.loads(urllib.urlopen(url).read())
	return response

def topicQuery():

	api_key = open("api_key.txt").read()
	service_url = 'https://www.googleapis.com/freebase/v1/topic'
	topic_id = '/m/0d6lp'
	params = {
	  'key': api_key,
	  'filter': 'suggest'
	}
	url = service_url + topic_id + '?' + urllib.urlencode(params)
	topic = json.loads(urllib.urlopen(url).read())
	return topic

def fileWrite(data, fileName):
	with open(fileName, 'w') as outfile:
		json.dump(data, outfile, sort_keys = True, indent = 4)
	

def main():
	searchResult = searchQuery()
	fileWrite(searchResult, 'search_response.txt')

	topicResult = topicQuery()
	fileWrite(topicResult, 'topic_response.txt')

if __name__ == '__main__':
	main()