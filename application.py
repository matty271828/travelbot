import requests
import json
import os
import time, datetime, dateutil
import pandas as pd
import concurrent.futures, threading

from helpers import finder

def search_oneway(source_array, destination_array, source_begin_date, source_end_date):
    """Function to search for one way flights between two destinations"""
    # Contact API for cheapest one way flights
    with concurrent.futures.ThreadPoolExecutor(max_workers=32) as executor:
        for single_date in daterange_source:
            for destination in destination_array:
                for source in source_array:
                    request_start = time.time()
                    executor.submit(cheapest_flight_finder.browseonewayQuotes,source, destination, single_date)

def search_return(source_array, destination_array, source_begin_date, source_end_date):
    """Function to search for return flights between two destinations"""
    # Contact API for cheapest one way flights
    with concurrent.futures.ThreadPoolExecutor(max_workers=64) as executor:
        for single_date in daterange_source:
            for destination in destination_array:
                for source in source_array:
                    request_start = time.time()
                    return_date = single_date + datetime.timedelta(days=5) 
                    executor.submit(cheapest_flight_finder.browsereturnQuotes, source, destination, single_date, return_date)

# Retrieve API key
api_key = os.environ.get("SKYSCANNER_API_KEY")

# Add headers
headers = {
    'x-rapidapi-host':"skyscanner-skyscanner-flight-search-v1.p.rapidapi.com",
    'x-rapidapi-key':api_key
}

# Airports where we can fly from
source_array = {"MAN-sky"} 
# Our destination airports
destination_array = {"NYCA-sky"}

# Dates
source_begin_date = pd.to_datetime("2021-09-05")
source_end_date =  pd.to_datetime("2021-09-20")
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

search_return(source_array, destination_array, source_begin_date, source_end_date)

# Stats on runtime
print("\nBenchmark Stats :")
print("Time spent in program: %f seconds"%(time.time()-function_start))

print("\nBenchmark Stats :")
print("Time spent in computing: %f seconds"%total_compute_time )
print("Time spent in requesting: %f seconds"%total_request_time )
print("Time spent in program: %f seconds"%(time.time()-function_start))
