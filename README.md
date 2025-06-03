# Prometheus (PaxMiner BB image puller)

## What is it?
Prometheus pulls BackBlast (BB) images saved on the F3 Database (PaxMiner) and saves them to an S3 Bucket. 
It is so named because in Greek mythology Prometheus steals fire from the gods and delivers it to humans.
(And I could name it anything I want since I wrote it!)

## !! Important !!
* Currently this code is written to work on AWS Lambda (hence the file `lambda_function.py`) but it could be 
modified to work with another service fairly easily.
* Modify the `configuration.py` file to make any modifications to the functionality of the app. Currently only four values can be configured:
  * S3_BUCKET - the S3 Bucket Name
  * LAST_PULLED_IMAGE_NAME_DOCUMENT - the name of a file that records the latest image pulled from PAXMiner so not all results need to be pulled into the app
  * MAX_FILES_IN_AO - how many images are allowed to be saved in each AO's file (and consequently put on the website)
  * SQL_QUERY_LIMIT - a limit on querying from PAXMiner so we don't make huge requests (will cycle through until it hits the image recorded in the LAST_PULLED_IMAGE_NAME_DOCUMENT

PAXMinder Database Credentials are environment variables set in the AWS Lambda.
