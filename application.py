import requests
import json
import os

api_key = os.environ.get("SKYSCANNER_API_KEY")

headers = {
    'x-rapidapi-host':"skyscanner-skyscanner-flight-search-v1.p.rapidapi.com",
    'x-rapidapi-key':api_key
}

origin = "BERL-sky"
destination = "LOND-sky"
currency = "GBP"
originCountry = "DE"
locale = "en-US"

myurl = "https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/browsequotes/v1.0/" + originCountry + "/" + currency + "/" + locale + "/"  + destination + "/" + origin + "/"+ "2021-07-22"
response = requests.request("GET", myurl, headers=headers)
print(response.text)