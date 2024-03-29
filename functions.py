import os
from run_sql import run_sql
from numpy.lib.utils import source
import pandas as pd
import concurrent.futures, threading
import time, datetime

from datetime import date
from classes import finder
from time import sleep

'''
This page handles functions for different flight formats. Edit the number of workers in order to speed up/slow done API contacting. 
A rate limit > 500 contacts/s will result in a response error and induce a 1 minute timeout. 
'''

show_testcode = 'no'

# minimum and maximum trip length by continent
triprange_bycontinent =  {"EU":(1,4),"NA":(5,12),"SA":(5,12),"AS":(5,12),"OC":(5,20),"AF":(3,10),"Unknown":(1,2)}

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
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        for single_date in daterange_source:
            for destination in destination_array:
                for source in source_array:
                    executor.submit(cheapest_flight_finder.browseonewayQuotes,source, destination, single_date)

def search_30dayoutward(source_array, destination_array, source_begin_date, source_end_date):
    '''Function to take one way flight data and find best return deals for each destination'''
    # Conduct a one way search, finding cheapest one way flights within date span
    search_oneway(source_array, destination_array, source_begin_date, source_end_date)

    # List to store outward flights
    outward_flights = []

    # Access DB and add cheapest outward flight for each dest. airport to dictionary
    # Retrieve list of unique destination airport names
    sql = "SELECT DISTINCT destination_id, dest FROM onewayflights"
    distinct_destinations = run_sql(sql)

    # For each distinct destination, added details of cheapest flight to outward_flights
    for i in range(0, len(distinct_destinations)):
        # Find cheapest flight for each destination
        sql = "SELECT origin_id, source, destination_id, dest, price, outdate FROM onewayflights WHERE dest = (%s) ORDER BY price ASC LIMIT 1"
        values = [distinct_destinations[i][1]]
        cheapest_flight = run_sql(sql, values)

        # reformat cheapest_flight as a dictionary
        flight_details = {"origin_id":cheapest_flight[0][0],"source":cheapest_flight[0][1],
        "destination_id":cheapest_flight[0][2],"dest":cheapest_flight[0][3],"price":cheapest_flight[0][4],
        "outdate":cheapest_flight[0][5]}

        # append to outward flights list
        outward_flights.append(flight_details)

    print(f"\nonewayflight search finished.\n")

    run_locationprocessing = 'no'
    # Run function to add airports never before encountered to place_info DB
    if run_locationprocessing == 'yes':
        process_places()

    # List to store return flights
    return_flights = []

    # For each outward flight, run return searches over the subsequent 30 days and save cheapest flight
    # Flight number limit, limits numbers of flights to run return search on in order to protect performance
    flight_number_limit = len(outward_flights)
    # Adjust this range to run return searches on more outward journeys
    for i in range(0, len(outward_flights)):
        # Start timer
        subloop_start_time = time.time()

        print(outward_flights[i])

        # Clear return_flights DB table
        sql = "DELETE FROM return_flights"
        clear_return_flights = run_sql(sql)
    
        # Configure initial return date & cheapest flight
        out_date = outward_flights[i]["outdate"]

        # Loop through 10 subsequent days from date of outward flight
        for j in range (5, 20):
            # Configure dates
            return_date = out_date + datetime.timedelta(days=j)

            # Contact API for cheapest return flights (this will insert into return_flights table in DB)
            cheapest_flight_finder.browsereturnQuotes(outward_flights[i]["origin_id"], outward_flights[i]["destination_id"], out_date, return_date)

            sleep(1)

        # Retrieve cheapest flight inserted into DB (SQL query will find the cheapest, no comparison needed in loop)
        sql = "SELECT origin_id, source, destination_id, dest, price, outdate, indate FROM return_flights ORDER BY price ASC LIMIT 1"
        cheapest_flight = run_sql(sql)

        # Output
        print(cheapest_flight)

        if cheapest_flight != []:
            # Add cheapest to return flights array
            return_flights.append(cheapest_flight)

            # SQL query to insert details of cheapest flight into DB
            sql = "INSERT INTO best_flights (origin_id, source, destination_id, dest, price, outdate, indate) VALUES (%s,%s,%s,%s,%s,%s,%s)"
            values = [cheapest_flight[0][0],cheapest_flight[0][1],cheapest_flight[0][2],cheapest_flight[0][3],cheapest_flight[0][4],cheapest_flight[0][5],cheapest_flight[0][6]]
            results = run_sql(sql, values)

        # Throttle programme
        # print('sleeping')
        # sleep(60)

        # Calculate time
        completion_time = time.time() - subloop_start_time
        print(f"subloop completed in {completion_time:.2f}s")

        est_time_remaining = ((flight_number_limit - i)*completion_time)/60
        print(f"estimated time remaining: {est_time_remaining:.2f}mins\n")
    
    print(return_flights)

def search_specificreturn(source, destination, out_date, return_date):
    '''Function to retrieve cheapest return flights between two specific destinations on a specific start and end date'''
    # Contact API for cheapest return flights

    cheapest_flight_finder.browsereturnQuotes(source, destination, out_date, return_date)
    

def search_30dayreturn(source_array, destination_array, source_begin_date, source_end_date):
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
                        executor.submit(cheapest_flight_finder.browsereturnQuotes, source, destination, single_date, return_date)

def process_places():
    '''Function to fill a database table with info on places'''
    # Retrieve one way flights found in this run from DB
    sql = "SELECT DISTINCT destination_id FROM onewayflights"
    unique_ids = run_sql(sql)

    # Run method on each id to add unique airports to place_info table in DB
    for i in range(0, len(unique_ids)):
        cheapest_flight_finder.submitPlaceInfo(unique_ids[i][0])
   
def search_oneyearreturn(source_array, destination_array):
    """Function to loop 30 day search over a one year period starting from today"""
    # Dates
    source_begin_date = pd.date.today()
    source_end_date = source_begin_date + datetime.timedelta(days=1)

    # Find dates of cheapest one way flights
    search_oneway(source_array, destination_array, source_begin_date, source_end_date)

    # For cheapest one way flights, run 30 day search to get best return journeys