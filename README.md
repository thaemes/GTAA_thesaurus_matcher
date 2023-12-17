# Matching server

A server that can match inputs to a GTAA (thesaurus identifier), using *fuzzy* matching. 

## Dependencies
It requires Python3 and Spacy:

```pip3 install spacy```

To install the spacy model do:

```python3 -m spacy download nl_core_news_lg``` 

## Overview
Introducing the different files 

### matching_server.py 
The actual server. It starts a socket server on the local host (127.0.0.1). If you send it a word, it will do the following: 

1. Try to do a direct match (This takes a few milliseconds)
2. If there is no direct match, it will use spacy to match it with word embeddings (this will take a few seconds). The server will send a notification about this to the client(```!slow matching```).
3. It returns matches to the client

### client_tester.py
A tester program. It connects to the server and you can type to test input strings. 

### open_subset_gtaas
A dictionary of GTAAs for the openly accessible part with video links. These are the terms that were assigned to ```sdo:about``` on clip leve. 

### blocklist.txt
List of words that will not be checked for matches. Words are separated by line. 

## TODO
- [ ] Document SPARQL query that can be used to retreive the GTAAs for a given subset. 
- [ ] Decide on functionality for longer sentences; should the literal matches be triggered, and return right away?