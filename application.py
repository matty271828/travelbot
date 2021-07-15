import requests
import json
import os
import time, datetime, dateutil
import pandas as pd

from functions import process_places, search_30dayreturn, search_oneway, search_30dayoutward, search_specificreturn
from run_sql import run_sql

# IATA country codes
IATA_Codes = {"AL","DZ","AS","AD","AO","AI","AG","AR","AM","AW","AU","AT","AZ","BS","BH","BD","BB","BY",
            "BE","BZ","BJ","BM","BT","BO","BW","BR","VG","BN","BG","BF","MM","BI","KH","CM","CA","CV",
            "KY","CF","TD","CL","CN","CO","CG","CD","CK","CR","CI","HR","CY","CZ","DK","DJ","DM","DO","EC",
            "EG","SV","GQ","ER","EE","ET","FO","FJ","FI","FR","GF","PF","GA","GM","GE","DE","GH","GI","GR",
            "GL","GD","GP","GU","GT","GN","GW","GY","HT","HN","HK","HU","IS","IN","ID","IE","IL","IT","CI",
            "JM","JP","JO","KZ","KE","KW","KG","LV","LB","LS","LI","LT","LU","MO","MK","MG","MW","MY","MV",
            "ML","MT","MH","MQ","MR","MU","MX","FM","MD","MC","MN","MS","MA","MZ","MM","NA","NP","NL","AN",
            "NC","NZ","NI","NE","NG","NO","OM","PK","PW","PA","PG","PY","PE","PH","PL","PT","US","QA","RE",
            "RO","RU","RW","MP","SM","SA","SN","SC","SL","SG","SK","SI","ZA","KR","ES","LK","KN","LC","VC",
            "SR","SZ","SE","CH","SY","TW","TZ","TH","TG","TT","TN","TR","TM","TC","AE","VI","US","UG","UA",
            "UK","UY","UZ","VU","VA","VE","VN","WF","YE","ZM","ZW"}


# Airports where we can fly from
source_array = {"LPL-sky", "MAN-sky"} 
# Our destination airports
destination_array = {"everywhere"}

# Dates
source_begin_date = pd.to_datetime("2021-09-01")
source_end_date =  pd.to_datetime("2021-09-05")

# Define max budget, enter as None if not wanted
max_budget = 20

# time request
total_compute_time = 0.0
total_request_time = 0.0

# Start timer
function_start = time.time()

# Clear all tables
sql = "DELETE FROM return_flights"
clear_return_flights = run_sql(sql)

sql = "DELETE FROM onewayflights"
clear_onewayflights = run_sql(sql)

sql = "DELETE FROM best_flights"
clear_best_flights = run_sql(sql)

#sql = "DELETE FROM place_info"
#clear_place_info = run_sql(sql)

search_30dayoutward(source_array, destination_array, source_begin_date, source_end_date, max_budget)

# Stats on runtime
print("\nBenchmark Stats :")
print("Time spent in program: %f seconds"%(time.time()-function_start))
