import requests, datetime, json
from time import sleep
import pycountry_convert as pc

from run_sql import run_sql

# Skyscanner response code dictionary
skyscanner_response_codes = {
                                200:"Success", 
                                204:"No Content - the session is still being created (wait and try again).",
                                301:"Moved Permanently – the result shows redirect location.",
                                304:"Not Modified – the results have not been modified since the last poll.",
                                400:"Bad Request -- Input validation failed.",
                                403:"Forbidden -- The API Key was not supplied, or it was invalid, or it is not authorized to access the service.",
                                410:"Gone – the session has expired. A new session must be created.",
                                429:"Too Many Requests – There have been too many requests in the last minute.",
                                500:"Server Error – An internal server error has occurred which has been logged."
}

class finder:
    def __init__(self, originCountry = "UK", currency = "GBP", locale = "en", rootURL="https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com"):
        self.currency = currency
        self.locale =  locale
        self.rootURL = rootURL
        self.originCountry = originCountry
        self.airports = {}
        self.skyscannercodes = {}
        
    def setHeaders(self, headers):
        self.headers =  headers
        self.createSession()

    # Create a session
    def createSession(self):
        self.session = requests.Session() 
        self.session.headers.update(self.headers)
        return self.session
        
    def browseonewayQuotes(self, source, destination, outdate, max_budget):
        self.trip_type = "oneway"
        quoteRequestPath = "/apiservices/browsequotes/v1.0/"

        browseonewayQuotesURL = self.rootURL + quoteRequestPath + self.originCountry + "/" + self.currency + "/" + self.locale + "/" + source + "/" + destination + "/" + outdate.strftime("%Y-%m-%d")
        # Use the same session to request again and again
        response = self.session.get(browseonewayQuotesURL)
        resultJSON = json.loads(response.text)

        # Check for good responses and print status code if unsuccessful
        if("Quotes" not in resultJSON):
            status = response.status_code
            print(f'{status}: {skyscanner_response_codes[status]}')

        # Pass info to print, 'None' given for return date
        self.printResult(resultJSON, outdate, None, max_budget)

    def browsereturnQuotes(self, source, destination, outdate, indate, max_budget):
        self.trip_type = "return"
        quoteRequestPath = "/apiservices/browsequotes/v1.0/"

        browsereturnQuotesURL = self.rootURL + quoteRequestPath + self.originCountry + "/" + self.currency + "/" + self.locale + "/" + source + "/" + destination + "/" + outdate.strftime("%Y-%m-%d") + "/" + indate.strftime("%Y-%m-%d")
        # Use the same session to request again and again
        response = self.session.get(browsereturnQuotesURL)
        resultJSON = json.loads(response.text)

        # Check for good responses and print status code if unsuccessful
        if("Quotes" not in resultJSON):
            status = response.status_code
            print(f'{status}: {skyscanner_response_codes[status]}')

            if status == 429:
                print('sleeping 1 min')
                sleep(60)

        self.printResult(resultJSON, outdate, indate, max_budget)

    def submitPlaceInfo(self, skyscanner_code):
        quoteRequestPath = "/apiservices/autosuggest/v1.0/"

        submitPlaceInfoURL = self.rootURL + quoteRequestPath + self.originCountry + "/" + self.currency + "/" + self.locale + "/" + "?query=" + skyscanner_code + "-sky"
        # Use the same session to request again and again
        response = self.session.get(submitPlaceInfoURL)
        resultJSON = json.loads(response.text)

        # Check for good responses and print status code if unsuccessful
        if("Places" not in resultJSON):
            status = response.status_code
            try:
                print(f'submitPlaceInfo API contact failure: {status}: {skyscanner_response_codes[status]}')
            except:
                print(status)

            if status == 429:
                print('sleeping 1 min')
                sleep(60)

        else:
            # Submit country of origin to database
            for Places in resultJSON["Places"]:
                # Determine continent of origin
                try:
                    country_code = pc.country_name_to_country_alpha2(Places["CountryName"], cn_name_format="default")
                    continent_name = pc.country_alpha2_to_continent_code(country_code)

                    # Insert location info for preprocessing and later use
                    #sql = "INSERT INTO place_info (skyscanner_code, placename, country, continent) VALUES (%s,%s,%s,%s) ON CONFLICT (skyscanner_code) DO NOTHING"
                    #values = [skyscanner_code, Places["PlaceName"], Places["CountryName"], continent_name]
                    #submitPlaceInfo = run_sql(sql, values)

                    # Insert location info for preprocessing and later use
                    sql = "INSERT INTO countries_continents (country, continent) VALUES (%s,%s) ON CONFLICT (country) DO NOTHING"
                    values = [Places["CountryName"], continent_name]
                    submitPlaceInfo = run_sql(sql, values)
                
                except:
                    # Continent has been left out here due to KeyError and needs to be manually inputted into DB
                    print(f'Invalid country name: {Places["CountryName"]}')
                    
                    #sql = "INSERT INTO place_info (skyscanner_code, placename, country, continent) VALUES (%s,%s,%s,%s) ON CONFLICT (skyscanner_code) DO NOTHING"
                    #values = [skyscanner_code, Places["PlaceName"], Places["CountryName"], "unknown"]
                    #submitPlaceInfo = run_sql(sql, values)

                    # Insert location info for preprocessing and later use
                    sql = "INSERT INTO countries_continents (country, continent) VALUES (%s,%s) ON CONFLICT (country) DO NOTHING"
                    values = [Places["CountryName"], "UNKNOWN"]
                    submitPlaceInfo = run_sql(sql, values)

    # A bit more elegant print
    def printResult(self, resultJSON, outdate, indate, max_budget):
        # Check for response
        if("Quotes" in resultJSON):
            for Places in resultJSON["Places"]:
                self.airports[Places["PlaceId"]] = Places["Name"]
                self.skyscannercodes[Places["PlaceId"]] = Places["SkyscannerCode"] 

            for Quotes in resultJSON["Quotes"]:
                # Check flight within budget, prevents out of budget flights printing/saving
                if (max_budget == None):
                    pass
                elif (Quotes["MinPrice"] > max_budget):
                    break

                # return trip
                if self.trip_type == "return":
                    # Retrieve trip info
                    source = Quotes["OutboundLeg"]["OriginId"]
                    dest = Quotes["OutboundLeg"]["DestinationId"]
                    price = Quotes["MinPrice"]

                    # Add trip info to SQL database, functions can then query these results
                    sql = "INSERT INTO return_flights (origin_id, source, destination_id, dest, price, outdate, indate) VALUES (%s,%s,%s,%s,%s,%s,%s)"
                    values = [self.skyscannercodes[source], self.airports[source], self.skyscannercodes[dest], self.airports[dest], price, outdate, indate]
                    results = run_sql(sql, values)

                    # Print trip info
                    print(outdate.strftime("%d-%b %a") + " - " + indate.strftime("%d-%b %a") + " | " + "%s  --> %s"%(self.airports[source],self.airports[dest]) + " | " + "%s GBP" %Quotes["MinPrice"])
                
                # one way trip
                else:
                    # Retrieve trip info
                    source = Quotes["OutboundLeg"]["OriginId"]
                    dest = Quotes["OutboundLeg"]["DestinationId"]
                    price = Quotes["MinPrice"]

                    # Add trip info to SQL database
                    sql = "INSERT INTO onewayflights (origin_id, source, destination_id, dest, price, outdate) VALUES (%s,%s,%s,%s,%s,%s)"
                    values = [self.skyscannercodes[source], self.airports[source], self.skyscannercodes[dest], self.airports[dest], price, outdate]
                    results = run_sql(sql, values)

                    # Print trip info
                    print(outdate.strftime("%d-%b %a") + " | " + "%s  --> %s"%(self.airports[source],self.airports[dest]) + " | " + "%s GBP" %Quotes["MinPrice"])

