import requests
import json
import os

api_key = os.environ.get("SKYSCANNER_API_KEY")

headers = {
    'x-rapidapi-host':"skyscanner-skyscanner-flight-search-v1.p.rapidapi.com",
    'x-rapidapi-key':api_key
}

# Airports where we can fly from: Berlin
source_array = {"LPL-sky"} 
# Our destination airports: Madrid, Barcelona, Seville, Valencia
destination_array = {"MAD-sky", "BCN-sky", "SVQ-sky", "VLC-sky"}



# And to make our life easier
rootURL = "https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/browsequotes/v1.0/"
currency = "GBP"
originCountry = "UK"
locale = "en-US"

airports = { }
for destination in destination_array:
    for source in source_array:
        myurl = rootURL + originCountry + "/" + currency + "/" + locale + "/" + source + "/"  + destination + "/" + "2021-09-01"
        response = requests.request("GET", myurl, headers=headers)
        temp = json.loads(response.text)
        
        # This checks if we have a quote or there were no flights
        if("Quotes" in temp):
            for Places in temp["Places"]:
                # Add the airport in the dictionary.
                airports[Places["PlaceId"]] = Places["Name"] 
            for Quotes in temp["Quotes"]:
                print("************")
                # print("%s --> to  -->%s" %(origin,destination))
                ori = Quotes["OutboundLeg"]["OriginId"]
                dest = Quotes["OutboundLeg"]["DestinationId"]
                # Look for Airports in the dictionary
                print("Journy:  %s  --> %s"%(airports[ori],airports[dest]))
                print("Price: %s GBP" %Quotes["MinPrice"])
