import os
import pandas as pd
import concurrent.futures, threading
import time, datetime, dateutil

from classes import finder

# Retrieve API key
api_key = os.environ.get("SKYSCANNER_API_KEY")

# Add headers
headers = {
    'x-rapidapi-host':"skyscanner-skyscanner-flight-search-v1.p.rapidapi.com",
    'x-rapidapi-key':api_key
}

# Retrieve function
cheapest_flight_finder = finder()
cheapest_flight_finder.setHeaders(headers)


def search_oneway(source_array, destination_array, source_begin_date, source_end_date):
    """Function to search for one way flights between two destinations"""
    # Configure dates
    daterange_source = pd.date_range(source_begin_date, source_end_date)

    # Contact API for cheapest one way flights
    with concurrent.futures.ThreadPoolExecutor(max_workers=32) as executor:
        for single_date in daterange_source:
            for destination in destination_array:
                for source in source_array:
                    request_start = time.time()
                    executor.submit(cheapest_flight_finder.browseonewayQuotes,source, destination, single_date)

def search_return(source_array, destination_array, source_begin_date, source_end_date):
    """Function to search for return flights between two destinations"""
    # Configure dates
    daterange_source = pd.date_range(source_begin_date, source_end_date)
    
    # Contact API for cheapest one way flights
    with concurrent.futures.ThreadPoolExecutor(max_workers=64) as executor:
        for single_date in daterange_source:
            for destination in destination_array:
                for source in source_array:
                    request_start = time.time()
                    return_date = single_date + datetime.timedelta(days=5) 
                    executor.submit(cheapest_flight_finder.browsereturnQuotes, source, destination, single_date, return_date)