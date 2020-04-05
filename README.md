# RDF-parser-normalizer

This respository shows initial workings for the following logic:

![image](https://user-images.githubusercontent.com/5884637/78472694-92585c80-7743-11ea-9d23-8f4128c5fa64.png)


Our sample input CSV file is sgoing to be of the following structure (e.g. describing github contributions) :

e.g. :

| Name | User | Github url | Number of Repos |
|---|---|---|---|
| Ilya Venger | vengeri | https://github.com/ivenger/ | 14 |
| Tony Hammond | tonyhammond | https://github.com/tonyhammond | 13 |


Step 1: Load example.csv file
using csv module 
Expected input is a basic csv file as per above. Output is a 

Step 2: Convert example.csv to rdf
convert-to-rdf.py
Use W3C recommendation from 2015 on CSV2RDF conversions:
https://www.w3.org/TR/csv2rdf/
and will use:
https://www.w3.org/TR/2015/REC-tabular-data-model-20151217/
https://w3c.github.io/csvw/csv2rdf/



