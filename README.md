# Prometheus (PaxMiner BB image puller)

## What is it?
Prometheus pulls BackBlast (BB) images saved on the F3 Database (PaxMiner) and saves them to an S3 Bucket. 
It is so named because in Greek mythology Prometheus steals fire from the gods and delivers it to humans.
(And I could name it anything I want since I wrote it!)

## !! Important !!
* Currently this code is written to work on AWS Lambda (hence the file `lambda_function.py`) but it could be 
modified to work with another service fairly easily.
* Modify the `configuration.py` file to make any modifications to the functionality of the app.