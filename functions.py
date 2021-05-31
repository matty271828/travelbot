import os
from numpy.lib.utils import source
import pandas as pd
import concurrent.futures, threading
import time, datetime, dateutil

from datetime import date
from classes import finder
from time import sleep
'''
This page handles functions for different flight formats. Edit the number of workers in order to speed up/slow done API contacting. 
A rate limit > 500 contacts/s will result in a response error and induce a 1 minute timeout. 
'''

show_testcode = 'yes'

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

def search_30dayreturn(source_array, destination_array, source_begin_date, source_end_date, max_budget):
    """Function to search for return flights between two destinations"""
    # Configure dates
    daterange_source = pd.date_range(source_begin_date, source_end_date)

    # Contact API for cheapest one way flights
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        for single_date in daterange_source:
            # Adjust sleep variable to slow down programme and avoid breaking API limit
            if show_testcode == 'yes':
                print("Sleeping for next date")

            sleep(2)
            for destination in destination_array:
                for source in source_array:
                    for i in range(1, 30):
                        # Throttle programme
                        if (i in [10, 20, 25]):
                            if show_testcode == 'yes':
                                print(f"sleeping {i}")
                            sleep(5)

                        elif (i in [26, 27, 28, 29]):
                            if show_testcode == 'yes':
                                print(f"sleeping {i}")
                            sleep(5)

                        # Execute worker    
                        return_date = single_date + datetime.timedelta(days=i) 
                        executor.submit(cheapest_flight_finder.browsereturnQuotes, source, destination, single_date, return_date, max_budget)
   
def search_oneyearreturn(source_array, destination_array, max_budget):
    """Function to loop 30 day search over a one year period starting from today"""
    # Dates
<<<<<<< HEAD
    source_begin_date = pd.date.today()
    source_end_date = source_begin_date + datetime.timedelta(days=1)

    # Find dates of cheapest one way flights
    search_oneway(source_array, destination_array, source_begin_date, source_end_date)

    # For cheapest one way flights, run 30 day search to get best return journeys

    
=======
    source_begin_date = date.today()

    # Populate list of start dates
    start_dates = []
    days_remaining = 365
    while days_remaining > 30:
        start_dates.append(source_begin_date)
        source_begin_date = source_begin_date + datetime.timedelta(days=30)
        days_remaining = days_remaining - 30

    # Initialise month count
    month_count = 1

    # Loop through 30 day periods
    for i in start_dates:
        # print message
        print(f"...Searching month {month_count}...starting date {i}")

        # Run 30 day search function
        source_end_date = i + datetime.timedelta(days=30)
        search_30dayreturn(source_array, destination_array, i, source_end_date, max_budget)

        # Add to month count
        month_count = month_count + 1
>>>>>>> 2440315c307f7b0cf560fd5b836f0c783ecce7f2
        