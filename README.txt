a. Names: Mingfei Ge(mg3534), Jialun Liu(jl4347)


=================================================================================
b. List of files we submit
=================================================================================
README.txt	
##### Configuration files #####			
actor_property.txt		
author_property.txt
businessperson_property.txt
entity.txt		
league_property.txt 
person_property.txt 
sportsteam_property.txt

##### main script #####	
infobox_MQL.py			

##### file for queries #####	
test_question.txt
test_info.txt

##### transcripts #####
transcript_infobox.txt
transcript_question.txt

=================================================================================
c. How to run our program
=================================================================================
1. python infobox_MQL.py -k <API KEY> -t <infobox|question> -q <query>
2. python infobox_MQL.py -k <API KEY> -t <infobox|question> -f <filename>


=================================================================================
d. Internal design of our project
=================================================================================
The program has two main steps. 1) Getting Freebase data based on predefined 
structures, 2) Print data with barline boundaries

1) The program first reads the "entity.txt" configuration:
/people/person
/book/author
/film/actor
/tv/tv_actor
/organization/organization_founder
/business/board_member
/sports/sports_league
/sports/sports_team
/sports/professional_sports_team

Which are actually six properties this project is interested in, like "Person", "Actor" etc.






2) The high idea to print data with barline is use template to format the printing
style. The part has two steps. First get values from stored data that extracted 
from Freebase API, then print it in with specific format.

i. Get values from stored data
	The simple case is to acquire value that stores data in dictionary. However,
	we also needs to deal with the case that we needs to preprocessing, for example
	, we needs to combine separate properties that 'spouse' has to generate an 
	one-line value. 

ii. Print with specific format
	We have define three format for printing. For the stored data that has a list
	of strings, we simply print values in the list one by one. Like the following:
	--------------------------------------------------------------------------------------------------
	| Books:          Business @ the Speed of Thought: Using a Digital Nervous System                  |
	|                 The Road Ahead                                                                   |
	|                 Open Letter to Hobbyists                                                         |
	 --------------------------------------------------------------------------------------------------
	For other data has contains a dictionary of values, we needs to automatically
	print the inside barline as the following:
	 ---------------------------------------------------------------------------------------------------
	|Leadership:      |Organization         |From/To            |Role               |Title              |
	|                 ----------------------------------------------------------------------------------
	|                 |Microsoft Corpor...  |1975-04-04/2000-...|Chief Executive ...|Chief Executive ...|
 	 ---------------------------------------------------------------------------------------------------
 	So here, we compute the length of each column first of all, then creat format
 	with those inside barline, and finally print data with this format.

=================================================================================
f. API Key
=================================================================================
AIzaSyDqQg19UvY-wFQD78Wbdh6oy7BbO3OyyOM

requests per second per user:
defualt number: 10


=================================================================================
g. Additional information
=================================================================================
1. We don't have interactive mode like the reference implementation.

2. For actors, we don't print out the tv_actor property

3. For queries like "NFL" where it has information about "League" and books written about the NFL would be
considered as both "League" and "Author". We designed it this way so that we could have more comprehensive
information about the query.

4. When certain information like "location" does not exist in the json response, we don't print it in the infobox.
However, for cases like "PlayerRoster" where it has multiple properties "From", "To" etc., we would leave the 
field blank if there is no data available. 