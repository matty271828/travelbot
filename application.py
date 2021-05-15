import requests
import json
import os
import time, datetime, dateutil
import pandas as pd
import concurrent.futures, threading

from helpers import finder

# Retrieve API key
api_key = os.environ.get("SKYSCANNER_API_KEY")

# Add headers
headers = {
    'x-rapidapi-host':"skyscanner-skyscanner-flight-search-v1.p.rapidapi.com",
    'x-rapidapi-key':api_key
}

# Airports where we can fly from: Berlin
source_array = {"UK-sky"} 
# Our destination airports: Madrid, Barcelona, Seville, Valencia
destination_array = {"JP-sky"}

# Dates
source_begin_date = "2021-06-05"
source_end_date =  "2021-06-08"  
daterange_source = pd.date_range(source_begin_date, source_end_date)
airports = { }

# time request
total_compute_time = 0.0
total_request_time = 0.0

# Retrieve function
cheapest_flight_finder = finder()
cheapest_flight_finder.setHeaders(headers)

# Start timer
function_start = time.time()

# Contact API for cheapest flights
with concurrent.futures.ThreadPoolExecutor(max_workers=32) as executor:
    for single_date in daterange_source:
        for destination in destination_array:
            for source in source_array:
                request_start = time.time()
                executor.submit(cheapest_flight_finder.browseQuotes,source, destination,single_date)

# Stats on runtime
print("\nBenchmark Stats :")
print("Time spent in program: %f seconds"%(time.time()-function_start))

print("\nBenchmark Stats :")
print("Time spent in computing: %f seconds"%total_compute_time )
print("Time spent in requesting: %f seconds"%total_request_time )
print("Time spent in program: %f seconds"%(time.time()-function_start))
