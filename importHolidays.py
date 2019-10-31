#!/usr/bin/env python3

import configparser
import datetime
import pprint
import psycopg2
import psycopg2.extras
import requests

# parse 3CX config
CONFIG = configparser.ConfigParser()
CONFIG.read('/var/lib/3cxpbx/Bin/3CXPhoneSystem.ini')

# connect 3CX-DB
DB = psycopg2.connect(\
	dbname = CONFIG.get('QMDatabase', 'DBName'),\
	user = CONFIG.get('CfgServerProfile', 'MasterDBUser'),\
	password = CONFIG.get('CfgServerProfile', 'MasterDBPassword'),\
	host = CONFIG.get('QMDatabase', 'DBHost'),\
	port = CONFIG.get('QMDatabase', 'DBPort')\
)
DBCUR = DB.cursor()

# get holidays from https://feiertage-api.de for current year
year = datetime.datetime.now().year
answer = requests.get(url = 'https://feiertage-api.de/api/', params = {'jahr' : year, 'nur_land' : 'BE'})
dataThis = answer.json()

# get holidays for next year
answer = requests.get(url = 'https://feiertage-api.de/api/', params = {'jahr' : year + 1, 'nur_land' : 'BE'})
dataNext = answer.json()

# prepare data for insert
data = []
for name in dataThis:
	date = dataThis[name]['datum'].split('-')
	data.append((date[0] + ' ' + name, 1, date[0], date[1], date[2], 0, date[0], date[1], date[2], 86340))

for name in dataNext:
	date = dataNext[name]['datum'].split('-')
	data.append((date[0] + ' ' + name, 1, date[0], date[1], date[2], 0, date[0], date[1], date[2], 86340))

#pprint.pprint(data)

# insert data into db
psycopg2.extras.execute_values(DBCUR, 'INSERT INTO holiday (name, fkidtenant, dtyear, dtmonth, dtday, dtseconds, end_dtyear, end_dtmonth, end_dtday, end_dtseconds) VALUES %s ON CONFLICT DO NOTHING', data)
DB.commit()

# TODO: delete old holidays?

# close connection to DB
DBCUR.close()
DB.close()
