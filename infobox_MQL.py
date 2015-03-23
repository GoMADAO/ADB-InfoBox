import json
import urllib
import sys

# For parse the input strings
from argparse import ArgumentParser

# For regular expression
import re
# To sort the list of dictionary by some key
from operator import itemgetter

# function to do Search API call
def searchQuery(query, api_key):

	service_url = 'https://www.googleapis.com/freebase/v1/search'
	params = {
	        'query': query,
	        'key': api_key
	}
	url = service_url + '?' + urllib.urlencode(params)
	response = json.loads(urllib.urlopen(url).read())
	return response

# function to do Topic API call
def topicQuery(topic_id, api_key):

	service_url = 'https://www.googleapis.com/freebase/v1/topic'
	params = {
	  'key': api_key,
	  'filter': 'all'
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

def infoExtractor(pattern, infoBox, topicResult):
	
	propertyDict = {}
	# If there is third level of information
	thirdLevel = False

	# Build a dictionary of the entities we are interested in
	with open(pattern,"r") as text:
		for line in text:
			prop = line.strip().split('-')
			# first is the key, last is the name of the property
			if len(prop) == 1:
				propName = prop[0].split('+')
				propertyDict[propName[0]] = propName[1]
			else:
				propertyDict[prop[0]] = {}
				for pair in prop[1:]:
					keyValue = pair.split('+') 
					propertyDict[prop[0]][keyValue[0]] = keyValue[1]

	#print propertyDict

	# Extract properties from the Topic API response
	for prop in propertyDict:
		if prop in topicResult['property']:
			temp = topicResult['property'][prop]
			#print prop
			#print "Pattern matching"
			if type(propertyDict[prop]) is dict:
				# array of "values"
				# multiple property needs to be extracted

				for subprop2 in propertyDict[prop]:
					matchObj = re.match(r'.*'+re.escape(propertyDict[prop][subprop2])+r'.*', subprop2, re.I)
					if matchObj:
						break

				# This "subprob2" should be the key of the array of dict.
				infoBox[propertyDict[prop][subprop2]] = []
				
				tempDict = {}

				for entry in temp['values']:
					temp2 = entry['property']
					
					for subprop in propertyDict[prop]:
						if subprop in temp2:
							if temp2[subprop]['values'] != []:
								tempDict[propertyDict[prop][subprop]] = temp2[subprop]['values'][0]['text']
							else:
								# Sometimes "To" don't have any value
								tempDict[propertyDict[prop][subprop]] = ''
					infoBox[propertyDict[prop][subprop2]].append(tempDict)
					tempDict = {}

			# When there is only one layer to go in order to read the data
			else:
				if 'valuetype' in temp:
					infoBox[propertyDict[prop]] = []
					for result in temp['values']:	
						if temp["valuetype"] != "object":
							infoBox[propertyDict[prop]].append(result['value'])
						else:
							infoBox[propertyDict[prop]].append(result['text'])

				
			
	
	#print infoBox

def printInfobox():	
	with open("infoBox.txt","r") as data_file:
		data = json.load(data_file)
	pprint(data)


# Do MQL query
def mqlQuery(query, api_key):

	service_url = 'https://www.googleapis.com/freebase/v1/mqlread'

	# We are only looking for two types -- Book and Organizations
	query1 = [{
	  	"/book/author/works_written": [{
	  	  "a:name": None,
	  	  "name~=": query
	  	}],
	  	"id": None,
	  	"name": None,
	  	"type": "/book/author",
	  	"limit": 1000
	}]
	params = {
	        'query': json.dumps(query1),
	        'key': api_key
	}
	url = service_url + '?' + urllib.urlencode(params)
	response = json.loads(urllib.urlopen(url).read())

	query2 = [{
       	"/organization/organization_founder/organizations_founded": [{
        "a:name": None,
        "name~=": query
	   	}],
	   	"id": None,
	   	"name": None,
	   	"type": "/organization/organization_founder"
	 }]
	params2 = {
	         'query': json.dumps(query2),
	         'key': api_key
	}
	url2 = service_url + '?' + urllib.urlencode(params2)
	response2 = json.loads(urllib.urlopen(url2).read())
	
	# return response
	return response

# Write JSON response to file
def jsonWrite(data, fileName):
	with open(fileName, 'w') as outfile:
		json.dump(data, outfile, sort_keys = True, indent = 4)

def printResponse(data, queryType):
	if queryType == 'book':
		key = '/book/author/works_written'
	elif queryType == 'organization':
		key = '/organization/organization_founder/organizations_founded'

	string = ''
	index = 0

	# sort the response according to the 'name'
	newlist = sorted(data['result'], key=itemgetter('name')) 

	# Construct the sentence and print in the console
	if newlist != []:
		for entry in newlist:
			index += 1
			string = str(index)+'. '+entry['name']+' (as Author) '+'created <'+entry[key][0]['a:name']+'>'
			if len(entry[key]) > 1:
				for book in range(1, len(entry[key])):
					string += ', <'+entry[key][book]['a:name']+'>'

			print string

def printRunFormat():
		print "Run the script by following format:"
		print "python infobox_MQL.py -k <Freebase API key> -q <query> -t <infobox|question>"
		print "python infobox_MQL.py -k <Freebase API key> -f <file of queries> -t <infobox|question>"	

def printEntityDict(entityDic, query):
	displayDic={'AUTHOR':False, 'BUSINESS_PERSON':False, 'ACTOR':False,
			'LEAGUE':False, 'SPORTS TEAM':False }
	for item in entityDic:
		if entityDic[item]['found']==True and item == '/sports/sports_league':
			displayDic['LEAGUE']=True
		if entityDic[item]['found']==True and item ==\
			'/sports/professional_sports_team':
			displayDic['SPORTS TEAM']=True
		if entityDic[item]['found']==True and item == '/book/author':
			displayDic['AUTHOR']=True
		if entityDic[item]['found']==True and item == '/tv/tv_actor':
			displayDic['ACTOR']=True
		if entityDic[item]['found']==True and item == '/film/actor':
			displayDic['ACTOR']=True
		if entityDic[item]['found']==True and item == '/business/board_member':
			displayDic['BUSINESS_PERSON']=True
		if entityDic[item]['found']==True and item ==\
		'/organization/organization_founder':
			displayDic['BUSINESS_PERSON']=True

	print ' ------------------------------------------------------'+\
			'---------------------------------------------'

	temp_str=''
	for item in displayDic:
		if displayDic[item]==True:
			temp_str+= item+','

	temp_str= query+'('+temp_str[0:len(temp_str)-1]+')'
	print '|'+'{:^99}'.format(temp_str)+'|'
	print ' ------------------------------------------------------'+\
			'---------------------------------------------'


def main():
	# Taking query from command line

	parser = ArgumentParser()

	parser.add_argument('-k', '--key', nargs=1, required=True,\
			dest="key", help='input API Key')
	parser.add_argument('-q', '--query', nargs='*', dest='query', help='input query')
	parser.add_argument('-t', '--type', nargs=1, dest='qtype', help='input query type')
	parser.add_argument('-f', '--file',  nargs=1, dest='filename', help='input filename')

	args=parser.parse_args()
	api_key = args.key
	querylist = args.query
	queryType = args.qtype
	filename = args.filename

	if filename ==None and querylist==None:
		printRunFormat()
		exit()

	api_key=''.join(api_key)
	query= ' '.join(querylist)
	queryType= ''.join(queryType)
	#filename=filename 
	

	if queryType == 'infobox':
		searchResult = searchQuery(query, api_key)
		jsonWrite(searchResult, 'search_response.txt')

		# To keep track of all the existing entities that we are interested in
		entityDict = {}
		# To store the information extracted from Topic API response
		infoBox = {}

	 	for result in searchResult['result']:
	 		topicResult = topicQuery(result['mid'], api_key)
			entityDict, match = matchEntity(topicResult['property']['/type/object/type']['values'])

			if match == True:
				break

		# test	
		printEntityDict(entityDict,query)
		jsonWrite(topicResult, 'topic_response.txt')

		infoExtractor('person_property.txt', infoBox, topicResult)

		infoExtractor('author_property.txt', infoBox, topicResult)

		infoExtractor('actor_property.txt', infoBox, topicResult)

		infoExtractor('businessperson_property.txt', infoBox, topicResult)

		infoExtractor('sportsteam_property.txt', infoBox, topicResult)

		infoExtractor('league_property.txt', infoBox, topicResult)

		jsonWrite(infoBox, 'infoBox.txt')

		printInfobox()

	elif queryType == 'question':

		matchObj = re.match(r'Who created (.*?)\?', query, re.I)
		query = matchObj.group(1)

		response = mqlQuery(query, api_key)

		printResponse(response, 'book')
		jsonWrite(response, 'book_mql.txt')
		# jsonWrite(response2, 'founder_mql.txt')
	

if __name__ == '__main__':
	main()
