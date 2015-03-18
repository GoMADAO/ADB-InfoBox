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

# Pass the topicResult['property']['/type/object/type']['values'](array) 
# into this function
def matchEntity(entities):
	entityDict = {}
	matchAny = False

	# Build a dictionary of the entities we are interested in
	with open("entity.txt","r") as text:
		entityDict = dict((line.strip(), {'found': False, 'entityType': ''}) for line in text)

	for entity in entities:
		if entity['id'] in entityDict:
			entityDict[entity['id']]['found'] = True
			entityDict[entity['id']]['entityType'] = entity['text']
			matchAny = True

	return entityDict, matchAny
	
# Write JSON response to file
def jsonWrite(data, fileName):
	with open(fileName, 'w') as outfile:
		json.dump(data, outfile, sort_keys = True, indent = 4)
	

def main():
	# Taking query from command line
	query = sys.argv[1]
	searchResult = searchQuery(query)
	jsonWrite(searchResult, 'search_response.txt')

	entityDict = {}
	# iteration = 0

 	for result in searchResult['result']:
 		topicResult = topicQuery(result['mid'])
		entityDict, match = matchEntity(topicResult['property']['/type/object/type']['values'])

		if match == True:
			break
		# iteration += 1

	print iteration, entityDict

	

	
	# print topicResult['property']
	# for var prop in topicResult:

	# First look into topicResult['property']['/type/object/type']


	jsonWrite(topicResult, 'topic_response.txt')

if __name__ == '__main__':
	main()