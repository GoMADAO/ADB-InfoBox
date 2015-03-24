a. Names: Mingfei Ge(mg3534), Jialun Liu(jl4347)


=================================================================================
b. List of files we submit
=================================================================================
README.txt				
actor_property.txt		
author_property.txt	Author 
businessperson_property.txt
entity.txt				
infobox_MQL.py			
league_property.txt	merge 
person_property.txt	Person 
sportsteam_property.txt
##### execute file



=================================================================================
c. How to run our program
=================================================================================
1. python infobox_MQL.py -k <API KEY> -t <infobox|question> -q <query>
2. python infobox_MQL.py -k <API KEY> -t <infobox|question> -f <filename>


=================================================================================
	How compile source code (If the above does not work)
=================================================================================



=================================================================================
d. Internal design of our project
=================================================================================
The program has two main steps. 1) Getting Freebase data based on predefined 
structures, 2) Print data with barline boundaries

1) // unfinished




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


=================================================================================
g. Additional information
=================================================================================

