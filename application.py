import requests
import json
import os
import time, datetime, dateutil
import pandas as pd
from helpers import findingCheapestFlights


api_key = os.environ.get("SKYSCANNER_API_KEY")

headers = {
    'x-rapidapi-host':"skyscanner-skyscanner-flight-search-v1.p.rapidapi.com",
    'x-rapidapi-key':api_key
}

# Airports where we can fly from: Berlin
source_array = {"LPL-sky"} 
# Our destination airports: Madrid, Barcelona, Seville, Valencia
destination_array = {"MAD-sky", "BCN-sky", "SVQ-sky", "VLC-sky"}

source_begin_date = "2021-09-18"
source_end_date =  "2021-09-24"  
daterange = pd.date_range(source_begin_date, source_end_date)
airports = { }
maxbudget = 40

cheapest_flight_finder = findingCheapestFlights()
cheapest_flight_finder.setHeaders(headers)

total_compute_time = 0.0
total_request_time = 0.0

function_start = time.time()
for single_date in daterange:
    for destination in destination_array:
        for source in source_array:
            request_start = time.time()
            resultJSON = cheapest_flight_finder.browseQuotes(source, destination,single_date)
            request_end = time.time()
            if("Quotes" in resultJSON):
                for Places in resultJSON["Places"]:
                    # Add the airport in the dictionary.
                    airports[Places["PlaceId"]] = Places["Name"] 
                for Quotes in resultJSON["Quotes"]:
                    if(Quotes["MinPrice"]<maxbudget):                        
                        print("************")
                        print(single_date.strftime("%d-%b %a"))
                        # print("%s --> to  -->%s" %(origin,destination))
                        source = Quotes["OutboundLeg"]["OriginId"]
                        dest = Quotes["OutboundLeg"]["DestinationId"]
                        # Look for Airports in the dictionary
                        print("Journy:  %s  --> %s"%(airports[source],airports[dest]))
                        print("Price: %s EUR" %Quotes["MinPrice"])
            calculation_end = time.time()
            total_compute_time += calculation_end - request_end 
            total_request_time += request_end - request_start

print("\nBenchmark Stats :")
print("Time spent in computing: %f seconds"%total_compute_time )
print("Time spent in requesting: %f seconds"%total_request_time )
print("Time spent in program: %f seconds"%(time.time()-function_start))
