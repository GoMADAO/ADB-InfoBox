import json
import urllib
import sys

# For parse the input strings
from argparse import ArgumentParser

# For regular expression
import re
# To sort the list of dictionary by some key
from operator import itemgetter

ALLOW_INDENT = 81

# function to do Search API call
def searchQuery(query, api_key):

	#api_key = open("api_key.txt").read()
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
def topicQuery(topic_id, api_key):

	#api_key = open("api_key.txt").read()
	service_url = 'https://www.googleapis.com/freebase/v1/topic'
	# topic_id = '/m/016z2j' # id of actor
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
	# infoBox = {}

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
				#print "multiple entries"
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
							#print subprop
							#print temp2[subprop]['values']
							if temp2[subprop]['values'] != []:
								tempDict[propertyDict[prop][subprop]] = temp2[subprop]['values'][0]['text']
							else:
								# Sometimes "To" don't have any value
								tempDict[propertyDict[prop][subprop]] = ''
					infoBox[propertyDict[prop][subprop2]].append(tempDict)
					tempDict = {}


			else:
				if 'valuetype' in temp:
					infoBox[propertyDict[prop]] = []
					for result in temp['values']:	
						if temp["valuetype"] != "object":
							# print temp['values'][0]['value']
							infoBox[propertyDict[prop]].append(result['value'])
						else:
							infoBox[propertyDict[prop]].append(result['text'])

					#print infoBox[propertyDict[prop]]	
	#print infoBox


# Do MQL query
def mqlQuery(query, api_key):
	#api_key = open("api_key.txt").read()
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

	newlist = sorted(data['result'], key=itemgetter('name')) 

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


def printInfobox(displayDic):	
	with open("infoBox.txt","r") as data_file:
		data = json.load(data_file)

	#people
	if displayDic['BUSINESS_PERSON'] == True or displayDic['ACTOR'] == True or\
		displayDic['AUTHOR'] == True:
		
		if data.has_key('Name'):
			printWithCrlf('Name', ''.join(data['Name']), ALLOW_INDENT)
		if data.has_key('Birthday'):
			printWithCrlf('Birthday', ''.join(data['Birthday']), ALLOW_INDENT)
		if data.has_key('Place of birth'):
			printWithCrlf('Place of birth', ''.join(data['Place of birth']), ALLOW_INDENT)

		#Death
		if data.has_key('Date of death') or data.has_key('Cause of death') or data.has_key('Place of death'):
			values={}
			param = []
			death = {'Date of death':'Date of death', 'Cause of death':'Cause of death',
					'Place of death':'Place of death'}
			if data.has_key('Date of death'):
				values['Date of death'] = ''.join(data['Date of death'])
			if data.has_key('Cause of death'):
				values['Cause of death'] = ''.join(data['Cause of death'])
			if data.has_key('Place of death'):
				values['Place of death'] = ''.join(data['Place of death'])
			param.append(values)
			printDict('Death', param , ALLOW_INDENT, death)

		#Sibling
		if data.has_key('Siblings'):
			sibling = {'Siblings':'Siblings'}
			printDict('Siblings', data['Siblings'] , ALLOW_INDENT, sibling)
		#Spouses
		if data.has_key('Spouse'):
			spouse = {'Name/From/To/Location':'Spouse/Marriage from/Marriage to/Marriage location'}
			printDict('Spouses', data['Spouse'] , ALLOW_INDENT, spouse)

		if data.has_key('Description'):
			printWithCrlf('Descriptions', ''.join(data['Description']), ALLOW_INDENT)
		

	#AUTHOR
	if displayDic['AUTHOR'] == True:
		
		if data.has_key('Books'):
			printListWithCrlf('Books', data['Books'], ALLOW_INDENT)
		if data.has_key('Books about'):
			printListWithCrlf('Books about', data['Books about'], ALLOW_INDENT)
		if data.has_key('Influenced people'):
			printListWithCrlf('Influenced', data['Influenced people'], ALLOW_INDENT)
		if data.has_key('Influenced by whom'):
			printListWithCrlf('Influenced by', data['Influenced by whom'], ALLOW_INDENT)


	#ACTOR
	if displayDic['ACTOR'] == True:
		
		#films
		if data.has_key('Film'):
			film = {'Film Name':'Film','Character':'Role'}
			printDict('Films', data['Film'] , ALLOW_INDENT, film)

	#BUSINESS_PERSON
	if displayDic['BUSINESS_PERSON'] == True:
		
		if data.has_key('Founded'):
			printListWithCrlf('Founded', data['Founded'], ALLOW_INDENT)
		if data.has_key('Leadership/Role'):
			leader = {'Organization':'Leadership Organization','Role':'Leadership/Role',\
			'Title':'Leadership Title', 'From/To':'Leadership From/Leadership To'}
			printDict('Leadership', data['Leadership/Role'] , ALLOW_INDENT, leader)
		if data.has_key('Membership/Role'):
			board = {'Organization':'membership organization', 'Role':'Membership/Role',\
			'Title':'membership title', 'From/To':'membership from/membership to'}
			printDict('Board Member', data['Membership/Role'] , ALLOW_INDENT, board)

	#LEAGUE
	if displayDic['LEAGUE'] == True:

		if data.has_key('Name'):
			printWithCrlf('Name', ''.join(data['Name']), ALLOW_INDENT)
		if data.has_key('Sport'):
			printWithCrlf('Sport', ''.join(data['Sport']), ALLOW_INDENT)
		if data.has_key('Slogan'):
			printWithCrlf('Slogan', ''.join(data['Slogan']), ALLOW_INDENT)
		if data.has_key('WebSite'):
			printWithCrlf('Official WebSite', ''.join(data['WebSite']), ALLOW_INDENT)
		if data.has_key('Championship'):
			printWithCrlf('Championship', ''.join(data['Championship']), ALLOW_INDENT)
		if data.has_key('Description'):
			printWithCrlf('Description', ''.join(data['Description']), ALLOW_INDENT)

	#SPORTS TEAM
	if displayDic['SPORTS TEAM'] == True:
		
		if data.has_key('Name'):
			printListWithCrlf('Name', data['Name'],ALLOW_INDENT)
		if data.has_key('Sport'):
			printListWithCrlf('Sport', data['Sport'],ALLOW_INDENT)
		if data.has_key('Arena'):
			printListWithCrlf('Arena', data['Arena'], ALLOW_INDENT)
		if data.has_key('Championships'):
			printListWithCrlf('Championships', data['Championships'], ALLOW_INDENT)
		if data.has_key('Founded'):
			printListWithCrlf('Founded', data['Founded'], ALLOW_INDENT)
		if data.has_key('Leagues'):
			league = {'Leagues':'Leagues'}
			printDict('Leagues', data['Leagues'] , ALLOW_INDENT, league)
		if data.has_key('Location'):
			printListWithCrlf('Location', data['Location'], ALLOW_INDENT)

		#Coach
		if data.has_key('Coach'):
			coach={"Name": "Coach","From/To": "Coach From/Coach To","Position": "Coach Position"}
			printDict('Coaches', data['Coach'] , ALLOW_INDENT, coach)
		#PlayersRoster ---- data poistion problem
		if data.has_key('Roster'):
			roster={'Name':'Roster','Position':'Roster Position','Number':'Roster Number',\
			'From/To':'Roster From/Roster To'}
			printDict('PlayerRoster', data['Roster'] , ALLOW_INDENT, roster)
		if data.has_key('Description'):
			printWithCrlf('Description', ''.join(data['Description']), ALLOW_INDENT)



def replValWithEll(value, allow_num):
	if len(value)>allow_num:
		value=value[:allow_num-3]+'...'
	return value

def printLineInDic(name, value, lenth, template):
	if lenth == 4:
		print template.format(name=name, key0=value[0].encode('utf-8'), key1=value[1].encode('utf-8'), \
			key2=value[2].encode('utf-8'), key3=value[3].encode('utf-8'))
	elif lenth == 3:
		print template.format(name=name, key0=value[0].encode('utf-8'), key1=value[1].encode('utf-8'), \
			key2=value[2].encode('utf-8'))
	elif lenth == 2:
		print template.format(name=name, key0=value[0].encode('utf-8'), key1=value[1].encode('utf-8'))
	elif lenth == 1:
		print template.format(name=name, key0=value[0].encode('utf-8'))

def preprocessFromTo(values, pattern):
	s = pattern.split('/')
	str_from=s[0]
	str_to=s[1]

	for item in values:
		temp=''
		if item.has_key(str_from):
			temp = item[str_from]+'/'
		else:
			temp ='---/'
		if item.has_key(str_to):
			temp +=item[str_to]
		else:
			temp +='now'
		item[pattern] = temp
	#print values
	return values

def preprocessSpouse(values, pattern):
	# hardcode pattern: Name/From/To/Location
	s = pattern.split('/')

	for item in values:
		temp = item[s[0]]
		if item.has_key(s[1]):
			temp = temp + ' ('+item[s[1]]+' -'
		else:
			temp = temp +' (??? -'
		if item.has_key(s[2]):
			if len(item[s[2]])!=0:
				temp = temp + ' '+item[s[2]] + ')'
			else:		
				temp = temp + ' now)'
		if item.has_key(s[3]):
			if len(item[s[3]])!=0:
				temp = temp + ' @ '+item[s[3]]
		item[pattern] = temp
	return values

def printDict(key, values, allow_num, cols):
	# hardcode pattern: From/To
	if values==[]:
		return

	if cols.has_key('From/To'):
		values = preprocessFromTo(values, cols['From/To'])

	if cols.has_key('Name/From/To/Location'):
		values = preprocessSpouse(values, cols['Name/From/To/Location'])

	lenth = len(cols)
	each = (allow_num - lenth + 1 )/lenth
	first = (allow_num - lenth + 1 ) % lenth + each
	ident = first
	name = key+':'

	template = ''
	header = list(cols)
	if lenth>1:
		template = '|{name:17}|'

		for i in range(0, lenth):
			template+='{key'+str(i)+':'+str(ident)+'}|'
			ident = each

		printLineInDic(name, header, lenth, template)
	
		name = ''
		print '|                 ----------------------------------------------------------------------------------'

	if lenth==1:
		template = '|{name:18}{key0:'+str(allow_num)+'}|'

	header = list(cols.values())
	#print header
	

	for item in values:
		templist=[]
		for val in header:
			if item.has_key(val):
				templist.append(replValWithEll(item[val], each))
			else:
				templist.append('')
		#print templist				
		printLineInDic(name, templist, lenth, template)
		name = ''
	
	print ' ---------------------------------------------------------------------------------------------------'


def printListWithCrlf(key, values, allow_num):
	name = key+':'
	template= '|{name:18}{value:'+str(allow_num)+'}|'
	for item in values:
		print template.format(name=name, value=replValWithEll(item, allow_num).encode('utf-8'))
		name = ''
	print ' ---------------------------------------------------------------------------------------------------'

def printWithCrlf(key, value, allow_num):
	temp = value.split('\n')
	value = ' '.join(temp)
	template= '|{name:18}{value:'+str(allow_num)+'}|'
	rest = len(value)
	name = key+':'
	while rest > allow_num:
		print template.format(name = name,value=value[0:allow_num].encode('utf-8'))
		name = ''
		value = value[allow_num:]
		rest -= allow_num
	print template.format(name = name, value= value.encode('utf-8'))
	print ' ---------------------------------------------------------------------------------------------------'

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

	print ' ---------------------------------------------------------------------------------------------------'

	temp_str=''
	for item in displayDic:
		if displayDic[item]==True:
			temp_str+= item+','

	temp_str= query+'('+temp_str[0:len(temp_str)-1]+')'
	print '|'+'{:^99}'.format(temp_str)+'|'
	print ' ------------------------------------------------------'+\
			'---------------------------------------------'
	#print displayDic
	return displayDic

def callAndPrint(api_key, query, queryType):
	'''
		
	'''
	if queryType == 'infobox':
		# query = "Robert Downey Jr."
		#print query
		searchResult = searchQuery(query, api_key)
		jsonWrite(searchResult, 'search_response.txt')

		# To keep track of all the existing entities that we are interested in
		entityDict = {}
		# To store the information extracted from Topic API response
		infoBox = {}

		# iteration = 0

	 	for result in searchResult['result']:
	 		topicResult = topicQuery(result['mid'], api_key)
			entityDict, match = matchEntity(topicResult['property']['/type/object/type']['values'])

			if match == True:
				break
			# iteration += 1

		#print entityDict

		displayDic=printEntityDict(entityDict,query)

		jsonWrite(topicResult, 'topic_response.txt')

		infoExtractor('person_property.txt', infoBox, topicResult)

		infoExtractor('author_property.txt', infoBox, topicResult)

		infoExtractor('actor_property.txt', infoBox, topicResult)

		infoExtractor('businessperson_property.txt', infoBox, topicResult)

		infoExtractor('sportsteam_property.txt', infoBox, topicResult)

		infoExtractor('league_property.txt', infoBox, topicResult)

		jsonWrite(infoBox, 'infoBox.txt')

		printInfobox(displayDic)

	elif queryType == 'question':
		# print query

		matchObj = re.match(r'Who created (.*?)\?', query, re.I)
		query = matchObj.group(1)

		# Get rid of the question mark
		# if query[-1] == '?':
		# 	query = query[:-1]
		#print query

		response = mqlQuery(query, api_key)

		printResponse(response, 'book')
		jsonWrite(response, 'book_mql.txt')
		# jsonWrite(response2, 'founder_mql.txt')


def main():

	'''
		ArgumentParser is used for get command line input
		It has four arugments. 
			'-k' stands for api key. 
			'-q' stands for query. 
			'-f' stands for filename
			'-t' stands for type
	'''
	# Define ArgumentParser
	parser = ArgumentParser()

	# Add argument options to ArgumentParser
	parser.add_argument('-k', '--key', nargs=1, required=True,\
			dest="key", help='input API Key')
	parser.add_argument('-q', '--query', nargs='*', dest='query', help='input query')
	parser.add_argument('-t', '--type', nargs=1, required=True, \
			dest='qtype', help='input query type')
	parser.add_argument('-f', '--file',  nargs=1, dest='filename', help='input filename')

	# Getting args from ArgumentParser
	args=parser.parse_args()
	api_key = args.key
	querylist = args.query
	queryType = args.qtype
	filename = args.filename

	# Checking valid of input type : cannot have both -q and -f
	if filename !=None and querylist!=None:
		printRunFormat()
		exit()

	# Checking valid of input type : cannot have None of both -q and -f 
	if filename ==None and querylist==None:
		printRunFormat()
		exit()

	# Taking api_key and type from command line
	api_key=''.join(api_key)	
	queryType= ''.join(queryType)
	
	# File: call functions iteratively 
	if filename != None and querylist == None:
		filename=''.join(filename)
		with open(filename,"r") as qfile:
			for line in qfile.readlines():
				line = line.strip()
				# Main function
				callAndPrint(api_key, line, queryType)

	# Query: call functions once
	if filename==None and querylist!=None:
		# Taking query from command line
		query= ' '.join(querylist)
		# Main function
		callAndPrint(api_key, query, queryType)
	

if __name__ == '__main__':
	main()
