#!/usr/bin/env python
# coding: utf-8

# **Load file with dialogue**

# In[17]:


from tkinter.filedialog import askopenfilename
from tkinter import Tk

Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
filename = askopenfilename()
print(filename)


# In[22]:


import csv

f = open(filename, 'r', encoding='utf-8-sig')

with f:

    reader = csv.reader(f)

    for row in reader:
        for e in row:
            print(e)

### For now assume that there are no row labels and column labels are simply given in row 1


# **We're going to generate readable .ttl directly**
# Future implementation would make it into proper rdflib objects and outputs that are flexible from a formatting perspective4

# In[30]:


output_prefixes = """
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix csvw: <http://www.w3.org/ns/csvw#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix tab: <http://tables> .
@prefix schem: <http://schemas/> .

@prefix csvw-ext: <http://csvw-ext#> .

csvw-ext: a owl:Ontology .

csvw-ext:isValueInRowNum a owl:DatatypeProperty;
    rdfs:label "is Value in Row Num";
    rdfs:comment "Relates a value to a certain row number in a table" ;
    rdfs:domain csvw:Cell ;
    rdfs:range xsd:integer ;
    rdfs:isDefinedBy csvw-ext: ;
    .

csvw-ext:isValueInColumnName a owl:DatatypeProperty;
    rdfs:label "is Value in Column Name";
    rdfs:comment "Relates a value to a certain column name in a table" ;
    rdfs:domain csvw:Cell ;
    rdfs:range xsd:string ;
    rdfs:isDefinedBy csvw-ext: ;
    .

csvw-ext:isValueInTable a owl:ObjectProperty;
    rdfs:label "is Value in Table";
    rdfs:comment "Relates a value to a certain table" ;
    rdfs:domain csvw:Cell ;
    rdfs:range csvw:Table ;
    rdfs:isDefinedBy csvw-ext: ;
    .    
    
"""


# Where we want to get to is something like this (assuming first row and COLUMN_LABEL1 and COLUMN_LABEL2 in TABLE_X and creating SCHEMA_X with values in 1:1 given as 'value_in_cell_11')
# 
# 
# This follows with some deviation the guidance on:
# (https://www.w3.org/TR/2015/REC-csv2rdf-20151217/)
# see csvw-ext: extension above. The basic rationale is to increase readability and direct linkage of cells to columns, rows and values.
# 
# 
# 
# ##### Once per table group
# ```sparql
# _:G a csvw:TableGroup .
# 
# ```
# 
# ##### Once for the table
# ```sparql
# _:T csvw:table _:G .       ## put the table in the TableGroup
# _:T a csvw:Table .         ## declares the table and puts it in a namespace
# _:T csvw:url :TABLE_X .    ## gives the table a URL
# 
# :SCHEMA_X a csvw:Schema         ## declares the schema we're going to be building out
# :TABLE_X csvw:tableSchema :SCHEMA_X  # I'd make the object property something like hasTableSchema; rather than tableSchema
# ```
# 
# ##### Go over each Column to build out the basic schema
# ```sparql
# _:column1 a csvw:Column .             ## Declare Column
# _:column1 csvw:column :SCHEMA_X .     ## Declare that the column forms part of the SCHEMA we are building
# _:column1 csvw:name "COLUMN_LABEL1" . ## Provide the canonical name for the column 
# 
# _:column2 a csvw:Column .
# _:column2 csvw:column :SCHEMA_X .      
# _:column2 csvw:name "COLUMN_LABEL2" .
# # etc.
# ```
# 
# ##### For each row in the table
# 
# ```sparql
# _:row1 csvw:row :TABLE_X .         ## Denotes that the row is in the Table
# _:row1 a csvw:Row .                ## declares the row
# _:row1 csvw:rownum 1^xsd:integer . ## marks the row number (start with 1)
# 
# ```
# 
# ##### For each cell at the intersection of the rows and columns (e.g. cell in row 1, column "Column 1")
# ```sparql
# _:cell11 a csvw:Cell .
# _:cell11 csvw-ext:isValueInRowID 1 .
# _:cell11 csvw-ext:isValueInColumnName "COLUMN_LABEL1" .
# _:cell11 csvw:describes "value_in_cell_11" .
# _:cell11 csvw-ext:isValueInTable :TABLE_X .
# 
# ```

# In[51]:


import urllib.parse

temp_table_name = "example"
table_url =  urllib.parse.quote(temp_table_name)


output_table = """
_:T csvw:table _:G .       
_:T a csvw:Table .         
_:T csvw:url tab:""" + table_url +" . "     


output_ttl = output_prefixes+output_table 
#test: print(output_ttl)

schema_url = "schem:SCHEMA_"+table_url

output_schema = """
"""+ schema_url + """ a csvw:Schema . 
tab:""" + table_url + """ csvw:tableSchema """ + schema_url+ """ .
"""

#test: print (output_schema)

output_ttl += output_schema
#test: print (output_ttl)

output_columns = ""
f = open(filename, 'r', encoding='utf-8-sig')
with f:

    reader = csv.reader(f)
    columns = next(reader)
    
#test: print(columns)
    i=1
    for col in columns:
        col_blank = "_:column"+str(i)
        output_columns += col_blank+""" a csvw:Column .
""" + col_blank + """ csvw:column """ + schema_url + """ . 
""" + col_blank + """ csvw:name """ + "\"" + col + "\"" + """ .
"""
        i = i+1
    
#test: print (output_columns)
output_ttl += output_columns 


output_rows = ""
f = open(filename, 'r', encoding='utf-8-sig')
with f:
    i=1
    reader = csv.reader(f)
    _blank = next(reader) # skip the first row
    j = 1
    for row in reader:
        row_blank = "_:row"+str(j)
        output_rows += row_blank+""" a csvw:Row .
""" + row_blank + """ csvw:row tab:""" + table_url + """ .
""" + row_blank + """ csvw:rownum """+ str(j)+""" .
"""
        j=j+1
        
# test: print (output_rows)      
output_ttl += output_rows

# print (output_ttl)


output_cells = ""
f = open(filename, 'r', encoding='utf-8-sig')
with f:
    i=1
    reader = csv.reader(f)
    col_labels = next(reader) # skip the first row
    j = 1
    for row in reader:
   #     print(row)
        k = 1
        for cell in row:
            cell_blank = "_:cell"+str(j)+str(k)
            output_cells += cell_blank+""" a csvw:Cell .
"""+cell_blank+""" csvw-ext:isValueInRowNum """+ str(j) + """ .
"""+cell_blank+""" csvw-ext:isValueInColumnName """+ "\"" + col_labels[k-1]+"\" ."+"""
"""+cell_blank+""" csvw:describes """+ "\""+cell+"\""+""" .
"""+cell_blank+""" csvw-ext:isValueInTable tab:""" + table_url + """ .
"""
#             print(col_labels[j-1])
            k=k+1
        j=j+1
            
#test: print(output_cells)
output_ttl += output_cells

print(output_ttl)


# Query 1:
# List all Column names
# ```sparql
# PREFIX csvw: <http://www.w3.org/ns/csvw#>
# select ?col where {
#     ?col_n a csvw:Column .
#     ?col_n csvw:name ?col
# }
# ```
# 
# 
# Query 2:
# List all values in column with a specific label (e.g. "Name")
# ```sparql
# PREFIX csvw: <http://www.w3.org/ns/csvw#>
# PREFIX csvw-ext: <http://csvw-ext#>
# select ?val where {
#     ?cell csvw-ext:isValueInColumnName "Name" .
#     ?cell csvw:describes ?val .
# }
# ```
# 
# Query 3:
# Return all pairs where values are matched in two columns (e.g. "Name" and "User")
# ```sparql
# PREFIX csvw-ext: <http://csvw-ext#>
# PREFIX csvw: <http://www.w3.org/ns/csvw#>
# select ?val1 ?val2 where { 
# 	?cell1 csvw-ext:isValueInColumnName "Name" .
#     ?cell1 csvw-ext:isValueInRowNum ?row_num .
#     ?cell1 csvw:describes ?val1 .
# 	?cell2 csvw-ext:isValueInColumnName "User" .
#     ?cell2 csvw-ext:isValueInRowNum ?row_num .
#     ?cell2 csvw:describes ?val2 .
# } 
# ```
# 
# In the next cell we are going to define a mapping for columns in the file.
# 
# 

# 
# Let's assume that we have the following example ontology for Bedrock:
# 
# ```sparql
# ex-ont: a owl:Ontology . 
# 
# ex-ont:Person a owl:Class ;
#     .
# ex-ont:Repository a owl:Class ;
#     .
# ex-ont:username a owl:DatatypeProperty ;
#     rdfs:domain ex-ont:Person ;
#     rdfs:range xsd:string ;
#     .
# ex-ont:numberOfRepositories a owl:DatatypeProperty ;
#     rdfs:domain ex-ont:Person ;
#     rdfs:range xsd:integer ;
#     .
#     
# ex-ont:hasRepository a owl:ObjectProperty ;
#     rdfs:domain ex-ont:Person ;
#     rdfs:range ex-ont:Repository ;
#     .
# ```
# 
# We would like to map the ontology to our columns as we had them above.
# Here's the rdf mapping file (**should be defined as valid CSV at a later time**)
# Let's recap what are the Column names in the file (run Query 1):
# 
# Name
# User
# Github url
# Number of Repos
# 
# For mapping we need to define a mapping ontology:
# 
# ```sparql
# onto-map: a owl:Ontology . 
# 
# onto-map:isMappedToClass a owl:ObjectProperty ;
#     rdfs:domain csvw:Column ;
#     rdfs:range owl:Class ;
#     rdfs:comment "Describes the mapping of a column to class" ;
#     .
# 
# onto-map:isLinkedTo a owl:ObjectProperty ;
#     rdfs:domain csvw:Column ;
#     rdfs:comment "An auxiliary property that allows to link between two columns" .
#     .
# 
# onto-map:isMappedToObjectProperty a owl:ObjectProperty ;
#     rdfs:domain onto-map:isLinkedTo ;
#     rdfs:range owl:ObjectProperty ;
#     rdfs:comment "Resolves the mapping of two columns that are Classes to ObjectProperty" ;
#     .
# ```
# 
# In RDF the Class mapping is going to look then like this:
# ```sparql
# _:col1 a csvw:Column .
# _:col1 csvw:column schem:SCHEMA_example .
# _:col1 csvw:name "Name" .
# _:col1 onto-map:isMappedTo ex-ont:Person .
# 
# _:col2 a csvw:Column .
# _:col2 csvw:column schem:SCHEMA_example .
# _:col2 csvw:name "User" .
# _:col2 onto-map:isMappedTo ex-ont:username .
# 
# _:col3 a csvw:Column .
# _:col3 csvw:column schem:SCHEMA_example .
# _:col3 csvw:name "Github url" .
# _:col3 onto-map:isMappedTo ex-ont:Repository .
# 
# _:col4 a csvw:Column .
# _:col4 csvw:column schem:SCHEMA_example .
# _:col4 csvw:name "Number of Repos" .
# _:col4 onto-map:isDataTypeMappedTo ex-ont:numberOfRepositories .
# 
# ```
# 
# In RDF the Object Property mapping of two columns to each other - equivalent to capturing some object property is going to look then like this:
# ```sparql
# _:map1 a csvw:Column .
# _:map1 csvw:column schem:SCHEMA_example .
# _:map1 csvw:name "Name" .
# 
# _:map2 a csvw:Column .
# _:map2 csvw:column schem:SCHEMA_example .
# _:map2 csvw:name "Github url" .
# 
# 
# _:map1 onto-map:isLinkedTo _:rel1 .
# _:map2 onto-map:isLinkedTo _:rel1 .
# _:rel1 onto-map:isMappedToObjectProperty ex-ont:hasRepository .
# ```
# 
# ### Still missing similar mapping for Datatype properties that are linked only to one 
# ***A bit more work to be done***
# 
# #### The combined ttl for the above then gives:
# 

# @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
# @prefix csvw: <http://www.w3.org/ns/csvw#> .
# @prefix skos: <http://www.w3.org/2004/02/skos/core#> .
# @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
# @prefix owl: <http://www.w3.org/2002/07/owl#> .
# @prefix prov: <http://www.w3.org/ns/prov#> .
# @prefix tab: <http://tables/> .
# @prefix schem: <http://schemas/> .
# @prefix ex-ont: <http://example-ontology/> .
# @prefix onto-map: <http://ontology-mapping/> .
# 
# 
# ex-ont: a owl:Ontology . 
# 
# ex-ont:Person a owl:Class ;
#     .
# ex-ont:Repository a owl:Class ;
#     .
# ex-ont:username a owl:DatatypeProperty ;
#     rdfs:domain ex-ont:Person ;
#     rdfs:range xsd:string ;
#     .
# ex-ont:numberOfRepositories a owl:DatatypeProperty ;
#     rdfs:domain ex-ont:Person ;
#     rdfs:range xsd:integer ;
#     .
#     
# ex-ont:hasRepository a owl:ObjectProperty ;
#     rdfs:domain ex-ont:Person ;
#     rdfs:range ex-ont:Repository ;
#     .
# 
# onto-map: a owl:Ontology . 
# 
# onto-map:isMappedToClass a owl:ObjectProperty ;
#     rdfs:domain csvw:Column ;
#     rdfs:range owl:Class ;
#     rdfs:comment "Describes the mapping of a column to class" ;
#     .
# 
# onto-map:isLinkedTo a owl:ObjectProperty ;
#     rdfs:domain csvw:Column ;
#     rdfs:comment "An auxiliary property that allows to link between two columns" ;
#     .
# 
# onto-map:isMappedToObjectProperty a owl:ObjectProperty ;
#     rdfs:domain onto-map:isLinkedTo ;
#     rdfs:range owl:ObjectProperty ;
#     rdfs:comment "Resolves the mapping of two columns that are Classes to ObjectProperty" ;
#     .
#     
# _:col1 a csvw:Column .
# _:col1 csvw:column schem:SCHEMA_example .
# _:col1 csvw:name "Name" .
# _:col1 onto-map:isMappedTo ex-ont:Person .
# 
# _:col2 a csvw:Column .
# _:col2 csvw:column schem:SCHEMA_example .
# _:col2 csvw:name "User" .
# _:col2 onto-map:isMappedTo ex-ont:username .
# 
# _:col3 a csvw:Column .
# _:col3 csvw:column schem:SCHEMA_example .
# _:col3 csvw:name "Github url" .
# _:col3 onto-map:isMappedTo ex-ont:Repository .
# 
# _:col4 a csvw:Column .
# _:col4 csvw:column schem:SCHEMA_example .
# _:col4 csvw:name "Number of Repos" .
# _:col4 onto-map:isMappedTo ex-ont:numberOfRepositories .
# 
# _:map1 a csvw:Column .
# _:map1 csvw:column schem:SCHEMA_example .
# _:map1 csvw:name "Name" .
# 
# _:map2 a csvw:Column .
# _:map2 csvw:column schem:SCHEMA_example .
# _:map2 csvw:name "Github url" .
# 
# 
# _:map1 onto-map:isLinkedTo _:rel1 .
# _:map2 onto-map:isLinkedTo _:rel1 .
# _:rel1 onto-map:isMappedToObjectProperty ex-ont:hasRepository .
# 
# 
# _:col1 onto-map:isLinkedTo _:rel1 .
# _:col2 onto-map:isLinkedTo _:rel1 .
# _:rel1 onto-map:isMappedToObjectProperty ex-ont:hasRepository .

# Query 4: show mappings betwen column names and ex-ont classes
# 
# ```sparql
# PREFIX csvw: <http://www.w3.org/ns/csvw#>
# PREFIX csvw-ext: <http://csvw-ext#>
# PREFIX onto-map: <http://ontology-mapping/>
# PREFIX ex-ont: <http://example-ontology/>
# 
# select distinct ?name ?map where {
#             ?col a csvw:Column .
#             ?col csvw:name ?name .
#             ?col onto-map:isMappedTo ?map .
# }
# ```
# 

# ### What is left now is to insert the data into a mapped graph with the relevant mappings in place
# 
# 
# 
# 

# In[15]:


starter:

PREFIX csvw: <http://www.w3.org/ns/csvw#>
PREFIX csvw-ext: <http://csvw-ext#>
PREFIX onto-map: <http://ontology-mapping/>
PREFIX ex-ont: <http://example-ontology/>
#construct {
#    ?val a ?map .
#}
#select ?val ?map 
where {
    ?cell csvw-ext:isValueInColumnName ?name .
    get_ipython().run_line_magic('pinfo', 'cell')
    {
        select distinct ?name ?map where {
            get_ipython().run_line_magic('pinfo', 'col')
            get_ipython().run_line_magic('pinfo', 'col')
            get_ipython().run_line_magic('pinfo', 'col')
        }
    }
}
    

