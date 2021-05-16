import requests
import json
import os
import time, datetime, dateutil
import pandas as pd

from functions import search_oneway, search_30dayreturn, search_oneyearreturn

# Airports where we can fly from
source_array = {"UK-sky"} 
# Our destination airports
destination_array = {"NYCA-sky"}

# Define max budget, enter as None if not wanted
max_budget = None

# time request
total_compute_time = 0.0
total_request_time = 0.0

# Start timer
function_start = time.time()

# Dates
source_begin_date = pd.to_datetime("2021-09-05")
source_end_date =  pd.to_datetime("2021-10-05")

search_30dayreturn(source_array, destination_array, source_begin_date, source_end_date, max_budget)

# Stats on runtime
print("\nBenchmark Stats :")
print("Time spent in program: %f seconds"%(time.time()-function_start))
