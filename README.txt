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
3. python infobox_MQL.py -k <API KEY>

A general note for question query:
Please follow the following pattern, otherwise you are going to break the program:

Who created xxxxxxx?

Any other query not in this format would lead to errors in pattern matching.


A note for the third option (interactive mode):
1. We tried to implement the interactive mode as close to the reference implementation as possible,
but they are not exactly the same.

2. When enter queries in this mode, wrap your query with double quotes, "Who created Microsoft?",
please don't forget the question mark, and this question mark issue applies to the first two 
implementations as well.

3. You can type "exit" to exit the program when the program is asking for query,
remember to wrap with double qutoes.


=================================================================================
d. Internal design of our project
=================================================================================
Part 1:

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
The program build a "entityDict" for that for later searching if the response from the
"Topic API" has at least one property that we are interested in, if not, it will just grab
the next result from the "Search API" and keep querying the "Topic API" until it is the case.

Once the program find a valid response from the "Topic API". It will start trying to extract
the information this project is interested in. Since all the types of the information this 
project is interested in is fixed, we just wrote separate configuration file for each property:

actor_property.txt			|	Actor
author_property.txt			|	Author
businessperson_property.txt	|	BusinessPerson
league_property.txt 		|	League
person_property.txt 		|	Person
sportsteam_property.txt 	|	SportsTeam

These configuration file are written in the way that it would tell the program how to extract
target information from the response of the "Topic API" and how to store these extracted informaton
in the dictionary "infoBox" for later print.

For example, if there is just one layer of dictionary we need to travel in order to get to the
target information from the "Topic API" response like the following:

/type/object/name+Name

"/type/object/name" is the key that we are looking for in the response, and the "Name" is the name
of the key the program is going to store in the infoBox.

Also, there are certain information that we need to travel two layers into the response dictionary
like the following:

/people/person/sibling_s-/people/sibling_relationship/sibling+Siblings

Where the first layer is "/people/person/sibling_s" and the second layer is
"/people/sibling_relationship/sibling". In this case, only the second layer entry would have a name
associated with it. After the program finds the information and try to store it in the infoBox,
it will try to store it like a list of subdictionaries like the following:

"Siblings": [
        {
            "Siblings": "Libby Gates"
        }, 
        {
            "Siblings": "Kristi Gates"
        }
    ], 

Where "Siblings" would be the key for both first and second layer. It is designed like this so that
for properties like "spouse" we can store multiple properties, e.g, "From", "To", "Marriage
location" in an unambiguous way:

/people/person/spouse_s-/people/marriage/spouse+Spouse-/people/marriage/from+Marriage from-/people/marriage/to+Marriage to-/people/marriage/location_of_ceremony+Marriage location

And the example resulted infoBox example would become:

"Spouse": [
        {
            "Marriage from": "1994-01-01", 
            "Marriage location": "Lanai", 
            "Marriage to": "", 
            "Spouse": "Melinda Gates"
        }
    ], 

Because we need to make sure that the "Spouse" would be the key for the first layer so that we could
actually try to print out the infoBox later. We used a little trick here. You should notice that 
only "/people/marriage/spouse+Spouse" has its name matches with part of its property. We used 
pattern matching to see if this is the case, that means we find the name of the key for this 
particular first layer.


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

Part 2:

For part 2, since the project is only interested in the "book" and "organization", we will just do two
MQL queries no matter what question we recieve, one for "book/author" and the other one for 
"/organization/organization_founder".

=================================================================================
f. API Key
=================================================================================
AIzaSyDqQg19UvY-wFQD78Wbdh6oy7BbO3OyyOM

requests per second per user:
defualt number: 10


=================================================================================
g. Additional information
=================================================================================
1. For actors, we don't print out the tv_actor property

2. For queries like "NFL" where it has information about "League" and books written about the NFL would be
considered as both "League" and "Author". We designed it this way so that we could have more comprehensive
information about the query.

3. When certain information like "location" does not exist in the json response, we don't print it in the infobox.
However, for cases like "PlayerRoster" where it has multiple properties "From", "To" etc., we would leave the 
field blank if there is no data available. 