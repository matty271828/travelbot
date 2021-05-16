import os
import pandas as pd
import concurrent.futures, threading
import time, datetime, dateutil

from classes import finder
from time import sleep
'''
This page handles functions for different flight formats. Edit the number of workers in order to speed up/slow done API contacting. 
A rate limit > 500 contacts/s will result in a response error and induce a 1 minute timeout. 
'''

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
                    executor.submit(cheapest_flight_finder.browseonewayQuotes,source, destination, single_date)

def search_return(source_array, destination_array, source_begin_date, source_end_date, max_budget):
    """Function to search for return flights between two destinations"""
    # Configure dates
    daterange_source = pd.date_range(source_begin_date, source_end_date)

    # Contact API for cheapest one way flights
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        for single_date in daterange_source:
            # Adjust sleep variable to slow down programme and avoid breaking API limit
            sleep(2)
            for destination in destination_array:
                for source in source_array:
                    for i in range(1, 30):
                        # Throttle programme
                        if i == 15:
                            print("sleeping")
                            sleep(5)
                        # Execute worker    
                        return_date = single_date + datetime.timedelta(days=i) 
                        executor.submit(cheapest_flight_finder.browsereturnQuotes, source, destination, single_date, return_date, max_budget)