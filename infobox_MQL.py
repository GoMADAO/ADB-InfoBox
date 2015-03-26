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


	# Extract properties from the Topic API response
	for prop in propertyDict:
		if prop in topicResult['property']:
			temp = topicResult['property'][prop]

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
	return response, response2

# Write JSON response to file
def jsonWrite(data, fileName):
	with open(fileName, 'w') as outfile:
		json.dump(data, outfile, sort_keys = True, indent = 4)

def printResponse(data, queryType, index):
	if queryType == 'book':
		key = '/book/author/works_written'
	elif queryType == 'organization':
		key = '/organization/organization_founder/organizations_founded'

	string = ''
	# index = 0

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

	return index

def printRunFormat():
		'''
			This function print possible options to use this program
		'''

		print "Run the script by following format:"
		print "python infobox_MQL.py -k <Freebase API key> -q <query> -t <infobox|question>"
		print "python infobox_MQL.py -k <Freebase API key> -f <file of queries> -t <infobox|question>"	


def printInfobox(displayDic):
	'''
		This function is the main function to print data in pretty format.
		It defines value as well as the order to print the data.
	'''
	with open("infoBox.txt","r") as data_file:
		data = json.load(data_file)

	#PEOPLE
	if displayDic['BUSINESS_PERSON'] == True or displayDic['ACTOR'] == True or\
		displayDic['AUTHOR'] == True:
		
		if data.has_key('Name') and displayDic['LEAGUE']==False and displayDic['SPORTS TEAM']==False:
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

		if data.has_key('Description') and displayDic['LEAGUE']==False and displayDic['SPORTS TEAM']==False:
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
	'''
		This function replace value with ellipsis, in order to suit print lenth.
		allow_num is the max number that could used for this value to print.

		value: value to be printed
		allow_num: max number that used for printing

	'''
	if len(value)>allow_num:
		value=value[:allow_num-3]+'...'
	return value

def printLineInDic(name, value, lenth, template):
	'''
		This function print a line in dic that extracted from Freebase.
		It has four options for different number of columns.
		The print method format by defined template.

		name: the title of a row
		value: a list that stores one line of data
		lenth: the number of columns
		template: print format 
	'''
	# print based on the number of columns
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
	'''
		This method combine From and To that are in separate key of extracted data.

		values: dic that stores extracted data
		pattern: that is the print format. For example, 'leader from/ leader to' 
				means leader start with 'leader from' and ends with 'leader to'
	'''
	s = pattern.split('/')
	str_from=s[0]
	str_to=s[1]

	for item in values:
		temp=''
		if item.has_key(str_from):
			temp = item[str_from]+'/'
		else:
			# print '---' in case 'From' is empty
			temp ='---/'
		if item.has_key(str_to):
			temp +=item[str_to]
		else:
			# print 'now' in case 'To' is empty
			temp +='now'
		item[pattern] = temp
	return values

def preprocessSpouse(values, pattern):
	'''
		This function combine Spouce 'Name/From/To/Location' into a value

		values: values stores the extracted data
		pattern: the print format. 
	'''
	# hardcode pattern: Name/From/To/Location
	s = pattern.split('/')

	for item in values:
		temp = ''
		# s[0] the 'Name' value
		if item.has_key(s[0]):
			temp = item[s[0]]
		else:
			temp = 'someone'
		# s[1] the 'From' value
		if item.has_key(s[1]):
			temp = temp + ' ('+item[s[1]]+' -'
		else:
			# print '???' in case 'From' is empty
			temp = temp +' (??? -'
		# s[2] the 'To' value
		if item.has_key(s[2]):
			if len(item[s[2]])!=0:
				temp = temp + ' '+item[s[2]] + ')'
			else:		
				# print 'now' in case 'To' is empty
				temp = temp + ' now)'
		# s[3] the 'Location' value
		if item.has_key(s[3]):
			if len(item[s[3]])!=0:
				temp = temp + ' @ '+item[s[3]]
		item[pattern] = temp
	return values

def printDict(key, values, allow_num, cols):
	'''
		This function print a dic values that are extracted from Freebase.
		The proper output is the following:

		|Leadership: |Organization         |From/To            |Role               |Title              |
		|            ----------------------------------------------------------------------------------
		|             Microsoft Corpor...  |1975-04-04/2000-...|Chief Executive ...|Chief Executive ...|

		The function creates header in the first, then print data in the corresponding column.
		There are three main steps:
			a) 	compute length of Characters that could use for a value to print,
				e.g. if 4 columns, we need to divide the total allow_num into 4. 
			b)	create print formt. format is a string that has bound symbols, key and length.
				e.g. ('|{key: length}|')
			c)	print the data.

		key: title of a row
		values: a dic that stores extracted data
		allow_num: max length of a row
		cols: dic that format keys in values

	'''
	# hardcode pattern: From/To
	if values==[]:
		return

	# preprocessing From/To and Name/From/To/Location
	if cols.has_key('From/To'):
		values = preprocessFromTo(values, cols['From/To'])

	if cols.has_key('Name/From/To/Location'):
		values = preprocessSpouse(values, cols['Name/From/To/Location'])

	# step a: compute length
	lenth = len(cols)
	each = (allow_num - lenth + 1 )/lenth
	# in case that dividend is divided with rest
	# first could has a little bit more length
	first = (allow_num - lenth + 1 ) % lenth + each
	ident = first

	# name is the title of row
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
	
	for item in values:
		templist=[]
		# Deal with a line of data, then print
		for val in header:
			if item.has_key(val):
				templist.append(replValWithEll(item[val], each))
			else:
				templist.append('')		
		printLineInDic(name, templist, lenth, template)
		name = ''
	
	print ' ---------------------------------------------------------------------------------------------------'


def printListWithCrlf(key, values, allow_num):
	'''
		This function print a list values that are extracted from Freebase.

		key: title of a row
		values: a dic that stores extracted data
		allow_num: max length of a row
	'''

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

def printRunFormat():
		print "Run the script by following format:"
		print "python infobox_MQL.py -k <Freebase API key> -q <query> -t <infobox|question>"
		print "python infobox_MQL.py -k <Freebase API key> -f <file of queries> -t <infobox|question>"	


def printEntityDict(entityDic, query):
	'''
		This function print title of a query. 

		entityDic: type that the query has
		query: query itself
	'''
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
	return displayDic


def callAndPrint(api_key, query, queryType):
	'''
		The main function that call Freebase to get data, then store data for further print.
	'''
	if queryType == 'infobox':

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

		matchObj = re.match(r'Who created (.*?)\?', query, re.I)
		query = matchObj.group(1)

		author, founder = mqlQuery(query, api_key)

		index = 0

		index = printResponse(author, 'book', index)
		jsonWrite(author, 'book_mql.txt')
		index = printResponse(founder, 'organization', index)
		jsonWrite(founder, 'founder_mql.txt')


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
