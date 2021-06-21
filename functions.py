import os
from run_sql import run_sql
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

show_testcode = 'no'

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


def search_oneway(source_array, destination_array, source_begin_date, source_end_date, max_budget):
    """Function to search for one way flights between two destinations"""
    # Configure dates
    daterange_source = pd.date_range(source_begin_date, source_end_date)

    # Contact API for cheapest one way flights
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        for single_date in daterange_source:
            for destination in destination_array:
                for source in source_array:
                    executor.submit(cheapest_flight_finder.browseonewayQuotes,source, destination, single_date, max_budget)

def search_30dayoutward(source_array, destination_array, source_begin_date, source_end_date, max_budget):
    '''Function to take one way flight data and find best return deals for each destination'''
    # Conduct a one way search, finding cheapest one way flights within date span
    search_oneway(source_array, destination_array, source_begin_date, source_end_date, max_budget)

    # List to store outward flights
    outward_flights = []

    # Access DB and add cheapest outward flight for each dest. airport to dictionary
    # Retrieve list of unique destination airport names
    sql = "SELECT DISTINCT dest FROM onewayflights"
    distinct_destinations = run_sql(sql)

    # For each distinct destination, added details of cheapest flight to outward_flights
    for i in range(0, len(distinct_destinations)):
        # Find cheapest flight for each destination
        sql = "SELECT origin_id, source, destination_id, dest, price, outdate FROM onewayflights WHERE dest = (%s) ORDER BY price ASC LIMIT 1"
        values = [distinct_destinations[i][0]]
        cheapest_flight = run_sql(sql, values)

        # reformat cheapest_flight as a dictionary
        flight_details = {"origin_id":cheapest_flight[0][0],"source":cheapest_flight[0][1],
        "destination_id":cheapest_flight[0][2],"dest":cheapest_flight[0][3],"price":cheapest_flight[0][4],
        "outdate":cheapest_flight[0][5]}

        # append to outward flights list
        outward_flights.append(flight_details)

    # For each outward flight, run search_return and save 
    for i in range(0, len(outward_flights)):
        print(outward_flights[i])

def search_specificreturn(source, destination, out_date, return_date, max_budget):
    '''Function to retrieve cheapest return flights between two specific destinations on a specific start 
    and end date'''
    # Contact API for cheapest one way flights
    
    source = "MAN-sky"
    destination = "JFK-sky"

    cheapest_flight_finder.browsereturnQuotes(source, destination, out_date, return_date, max_budget)
    

def search_30dayreturn(source_array, destination_array, source_begin_date, source_end_date, max_budget):
    """Function to search for return flights between two destinations"""
    # Configure dates
    daterange_source = pd.date_range(source_begin_date, source_end_date)

    # Contact API for cheapest one way flights
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
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
    source_begin_date = pd.date.today()
    source_end_date = source_begin_date + datetime.timedelta(days=1)

    # Find dates of cheapest one way flights
    search_oneway(source_array, destination_array, source_begin_date, source_end_date)

    # For cheapest one way flights, run 30 day search to get best return journeys

    
        