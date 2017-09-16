import sys
import psycopg2

# Since I want all data retained, I make sure we create a new fact table for each import
# There is a lot of future work to be done here: 
# Dimensions and Previous import detection are the big ones
def prepareTestCase():
	dbConnection = psycopg2.connect(host="localhost",database="postgres",user=dbUserName,password=dbPassword)
	dbConnection.set_session(autocommit=True)

	dbCursor = dbConnection.cursor()

	#If this is our first rodeo, create the table
	sqlCommand = """CREATE TABLE IF NOT EXISTS dim_testSequence 
		( 
			testSequenceID serial primary key, 
			testSequenceDesc int 
		)"""

	dbCursor.execute(sqlCommand)

	#Need to know the number of the last test case run
	sqlCommand = "SELECT max(testSequenceDesc) FROM dim_testSequence"

	dbCursor.execute(sqlCommand)

	testCaseNum = dbCursor.fetchone()[0]
	
	#If we didn't get anything, the table is empty and we start @ 1, otherwise we have now started the next test
	if testCaseNum is None:
		sqlCommand = "INSERT INTO dim_testSequence(testSequenceDesc) VALUES (1)"
		testCaseNum = 1
	else:
		testCaseNum = testCaseNum + 1
		sqlCommand = "INSERT INTO dim_testSequence(testSequenceDesc) VALUES (" + str(testCaseNum) + ")"

	dbCursor.execute(sqlCommand)

	dbCursor.close()
	dbConnection.close()
	return testCaseNum;

# Get the data from stdin and push it into the database
def importData(testCaseNum):
	dbConnection = psycopg2.connect(host="localhost",database="postgres",user=dbUserName,password=dbPassword)
	dbConnection.set_session(autocommit=True)

	dbCursor = dbConnection.cursor()
	
	recordsRejected = 0
	
	#Create our fact table, since it won't exist
	sqlCommand = "CREATE TABLE IF NOT EXISTS fact_inputfile" + str(testCaseNum) + " ( "

	for i in range(0, len(columnHeaders) - 1):
		sqlCommand += columnHeaders[i] + " varchar(255),\n"

	sqlCommand = sqlCommand + "value int )"
	dbCursor.execute(sqlCommand)

	#Read in the data from stdin, and do a simple sanity check (right amount of rows, value is an aggregatable number)
	for line in sys.stdin.readlines():
		if len(line.split("\t")) != len(columnHeaders) or line.split("\t")[len(columnHeaders) - 1].strip().isdigit() == False:
			#We want to count rejected records to at least inform the user that we didn't bring in everything
			#Future work would be piping these rejects to a file so they could be analyzed
			recordsRejected += 1
		else:
			#Format the input into a sql statement, probably better done w/ regex but this was quicker to think through
			input = "\'" + (line.replace("\t","\',\'",len(columnHeaders)-2)).replace("\t","\',").strip()
			sqlCommand = "INSERT INTO fact_inputfile" + str(testCaseNum) + " VALUES (" + input + ")"
			dbCursor.execute(sqlCommand)

	dbCursor.close()
	dbConnection.close()
	return recordsRejected;

# By doing the ETL, the rollup is now trivial, create a select statement w/ a group by and order by
def rollupData(testCaseNum, columnHeaders):
	dbConnection = psycopg2.connect(host="localhost",database="postgres",user=dbUserName,password=dbPassword)
	dbConnection.set_session(autocommit=True)

	dbCursor = dbConnection.cursor()

	# Manufacture the requested select statement
	sqlCommand = "SELECT " + columnHeaders[0]
	sqlTrailer = "GROUP BY " + columnHeaders[0]
	sqlCaboose = " ORDER BY " + columnHeaders[0]
	outputHeader = columnHeaders[0] + "\t"
	
	#We build the header and the sql statement at the same time... Probably a better way to do this but I didn't see it immediately
	for col in range(1, len(columnHeaders)):
		outputHeader = outputHeader + columnHeaders[col] + "\t"
		sqlCommand = sqlCommand + ", " + columnHeaders[col]
		sqlTrailer = sqlTrailer + ", " + columnHeaders[col]
		sqlCaboose = sqlCaboose + ", " + columnHeaders[col]
	outputHeader = outputHeader + "value"
	sqlCommand = sqlCommand + ", sum(value) FROM fact_inputfile" + str(testCaseNum) + " " + sqlTrailer + sqlCaboose
	
	# If the user asked for a column that didn't exist, we catch that and let them know
	try:
		dbCursor.execute(sqlCommand)
	except (Exception, psycopg2.ProgrammingError) as e:
		print "Error in provided arguments: " + str(e).partition("\n")[0];
		sys.exit(0)
	
	row = dbCursor.fetchone()
	
	#Otherwise, print it out like we brought it in, tab separated.
	print outputHeader;
	while row is not None:
		for value in row:
			print str(value) + "\t",
		print
		row = dbCursor.fetchone()

	dbCursor.close()
	dbConnection.close()
	return 1;

#Some constants for the db connection
dbUserName="rcarter"
dbPassword="rcarter"

# First get the header from stdin so we know what columns we're dealing with
# Also, trim the whitespace from the front and back, if any, to avoid typos in input
inputHeader = str.strip(sys.stdin.readline())

# If you're going to run multiple test cases, create a database for each to keep them separated.
testCase = 0

# Before we do anything, lets make sure the request makes sense.
columnHeaders = (inputHeader.split('\t'))

if (len(sys.argv) > len(columnHeaders)):
	print("Error: Number of arguments requested larger than number of input column headers. Terminating")
	sys.exit(0)

# Connect to the database and determine position in test sequence
testCase = prepareTestCase()

# Import the data into the database
rejects = importData(testCase)

# Provide the required output, handle situation where no headers were provided
if len(sys.argv) > 1:
	rollupData(testCase, sys.argv[1:])
else:
	rollupData(testCase, columnHeaders[:len(columnHeaders) - 1])

# Print warning to stderr that lets user know if there were problems.
if rejects > 0:
	print >> sys.stderr, "Warning: " + str(rejects) + " record(s) were rejected due to improper formatting/content"
