S3_BUCKET = "f3pugetsound-slack-pictures"

# the name of the file on S3 (in the root directory) that lets Prometheus know not to query beyond
LAST_PULLED_IMAGE_NAME_DOCUMENT = "last_file.txt"

# the number of files kept in S3 per AO
MAX_FILES_IN_AO = 260

# the number of results requested from an executed query from PaxMiner
SQL_QUERY_LIMIT = 10
