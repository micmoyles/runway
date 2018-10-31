# runway
python infra designed to 
* source data from external providers via network and web sockets
* store raw data onto backend servers
* parse raw data and load to databases

The databases are created and configured by a puppet module

Separate code for hanger which performs the analysis on stored data and generates the web front end.