# Wiki Search Engine
This Wiki search engine works on index produced using wikipedia dump file(english language).
To produce index:
```py
  python indscal.py dumpname indexname 
```
To search queries:
```py
  python search.py "query(with quotes)" 
```
Query for different fields should be separated using ','
example: "C:Dog,B:Dog"
or can be plain query
example: "Dog"
