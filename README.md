# RDF-parser-normalizer

This respository shows initial workings for the following logic:

![image](https://user-images.githubusercontent.com/5884637/78472694-92585c80-7743-11ea-9d23-8f4128c5fa64.png)


Our sample input CSV file is sgoing to be of the following structure (e.g. describing github contributions) :

e.g. :

| Name | User | Github url | Number of Repos |
|---|---|---|---|
| Fred Flintstone | flintstonef | https://github.com/flintstone/ | 14 |
| Barney Rubble | barneyrubble | https://github.com/awesomebarney | 11 |



Main Notebook file:
https://github.com/ivenger/RDF-parser-normalizer/blob/master/csv-import-read.ipynb



Use W3C recommendation from 2015 on CSV2RDF conversions:
https://www.w3.org/TR/csv2rdf/
and will use:
https://www.w3.org/TR/2015/REC-tabular-data-model-20151217/
https://w3c.github.io/csvw/csv2rdf/



see also:
https://github.com/CLARIAH/COW
