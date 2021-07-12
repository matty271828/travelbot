import requests
import json
import os
import time, datetime, dateutil
import pandas as pd

from functions import preprocess_places, search_30dayreturn, search_oneway, search_30dayoutward, search_specificreturn
from run_sql import run_sql

# Airports where we can fly from
source_array = {"UK-sky"} 
# Our destination airports
destination_array = {"everywhere"}

# Dates
source_begin_date = pd.to_datetime("2021-09-01")
source_end_date =  pd.to_datetime("2021-09-05")

# Define max budget, enter as None if not wanted
max_budget = None

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
#clear_best_flights = run_sql(sql)

#sql = "DELETE FROM place_info"
#clear_place_info = run_sql(sql)

search_30dayoutward(source_array, destination_array, source_begin_date, source_end_date, max_budget)

# Stats on runtime
print("\nBenchmark Stats :")
print("Time spent in program: %f seconds"%(time.time()-function_start))
