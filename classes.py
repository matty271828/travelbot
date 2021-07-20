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

budgets_by_continent = {"EU":10,"NA":200,"SA":300,"AS":200,"OC":350,"AF":200,"Unknown":0}

class finder:
    def __init__(self, originCountry = "UK", currency = "GBP", locale = "en", rootURL="https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com"):
        # set parameters
        self.currency = currency
        self.locale =  locale
        self.rootURL = rootURL
        self.originCountry = originCountry
        self.airports = {}
        self.skyscannercodes = {}

        # run SQL query to find airports already in place_info DB
        sql = "SELECT skyscanner_code FROM place_info"
        self.processedairports = run_sql(sql)
        
    def setHeaders(self, headers):
        self.headers =  headers
        self.createSession()

    # Create a session
    def createSession(self):
        self.session = requests.Session() 
        self.session.headers.update(self.headers)
        return self.session
        
    def browseonewayQuotes(self, source, destination, outdate):
        '''
        Method contacts API and retrieves JSON file of one way quotes between given locations and within dates.
        JSON file is then to be reviewed and information submitted to DB using DBsubmission method. 
        '''
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

        # Submit to DB, 'None' given for return date, this also handles printing
        self.DBsubmission(resultJSON, outdate, None)

        # Pass info to print, 'None' given for return date
        # self.printResult(resultJSON, outdate, None)

    def browsereturnQuotes(self, source, destination, outdate, indate):
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

        self.printResult(resultJSON, outdate, indate)

    def DBsubmission(self, resultJSON, outdate, indate):
        # Check for response
        if("Quotes" in resultJSON):
            for Places in resultJSON["Places"]:
                self.airports[Places["PlaceId"]] = Places["Name"]
                self.skyscannercodes[Places["PlaceId"]] = Places["SkyscannerCode"] 

            for Quotes in resultJSON["Quotes"]:
                # Retrieve trip info
                source = Quotes["OutboundLeg"]["OriginId"]
                dest = Quotes["OutboundLeg"]["DestinationId"]
                price = Quotes["MinPrice"]

                # Retrieve continent of destination and retrieve continental price limit
                while True:
                    try:
                        sql = "SELECT continent FROM place_info WHERE skyscanner_code = (%s)"
                        values = [self.skyscannercodes[dest]]
                        destination_continent = run_sql(sql,values)
                        continental_budget = budgets_by_continent[destination_continent[0][0]]
                        break
                    
                    except:
                        # destination was not found in place_info, run submit_placeinfo method
                        self.submitPlaceInfo(self.skyscannercodes[dest])

                # return trip
                if self.trip_type == "return":
                    if price < (2*continental_budget):
                        # Add trip info to SQL database, functions can then query these results
                        sql = "INSERT INTO return_flights (origin_id, source, destination_id, dest, price, outdate, indate) VALUES (%s,%s,%s,%s,%s,%s,%s)"
                        values = [self.skyscannercodes[source], self.airports[source], self.skyscannercodes[dest], self.airports[dest], price, outdate, indate]
                        results = run_sql(sql, values)

                        # Print trip info
                        print(outdate.strftime("%d-%b %a") + " - " + indate.strftime("%d-%b %a") + " | " + "%s  --> %s"%(self.airports[source],self.airports[dest]) + " | " + "%s GBP" %Quotes["MinPrice"])
                
                # one way trip
                else:
                    # Add trip info to SQL database
                    if price < continental_budget:
                        sql = "INSERT INTO onewayflights (origin_id, source, destination_id, dest, price, outdate) VALUES (%s,%s,%s,%s,%s,%s)"
                        values = [self.skyscannercodes[source], self.airports[source], self.skyscannercodes[dest], self.airports[dest], price, outdate]
                        results = run_sql(sql, values)

                        # Print trip info
                        print(outdate.strftime("%d-%b %a") + " | " + "%s  --> %s"%(self.airports[source],self.airports[dest]) + " | " + "%s GBP" %Quotes["MinPrice"])

    def submitPlaceInfo(self, skyscanner_code):
        '''
        This method is exclusively used to submit location information to the DB table place_info. 
        In turn this table is used to store info on what continents airports are located on. 
        It is not intended to be ran every time the program is used.
        '''
        quoteRequestPath = "/apiservices/autosuggest/v1.0/"

        # Use flag variable to register if airport already present in DB preprocessing
        code_present = 'no'
        for i in range(0, len(self.processedairports)):
            if skyscanner_code == self.processedairports[i][0]:
                code_present = 'yes'
            else:
                pass

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
            # Retrieve list of skyscanner codes already in DB
            sql = "SELECT skyscanner_code FROM place_info"
            existing_codes = run_sql(sql)

            # Submit specific airport location info to database
            for Places in resultJSON["Places"]:
                # Get values
                airport = Places["PlaceName"]
                country = Places["CountryName"]
                skyscanner_code = Places["PlaceId"][:-4]

                # check if skyscanner_code already in DB
                code_present = 'no'
                for i in range(0, len(existing_codes)):
                    if existing_codes[i][0] == skyscanner_code:
                        print(f'{skyscanner_code} already in DB')
                        code_present = 'yes'

                if code_present == 'no':
                    # Determine continent of origin
                    try:
                        country_code = pc.country_name_to_country_alpha2(Places["CountryName"], cn_name_format="default")
                        continent_name = pc.country_alpha2_to_continent_code(country_code)
                    except:
                        continent_name = 'Unknown'

                    # Insert location info for preprocessing and later use
                    sql = "INSERT INTO place_info (skyscanner_code, placename, country, continent) VALUES (%s,%s,%s,%s)"
                    values = [skyscanner_code, Places["PlaceName"], Places["CountryName"], continent_name]
                    submitPlaceInfo = run_sql(sql, values)
                    print(f"\nAdded to place_info: {skyscanner_code}: {airport}, {country}, {continent_name}\n")
            
    # A bit more elegant print
    def printResult(self, resultJSON, outdate, indate):
        # Check for response
        if("Quotes" in resultJSON):
            for Places in resultJSON["Places"]:
                self.airports[Places["PlaceId"]] = Places["Name"]
                self.skyscannercodes[Places["PlaceId"]] = Places["SkyscannerCode"] 

            for Quotes in resultJSON["Quotes"]:
                # Retrieve trip info
                source = Quotes["OutboundLeg"]["OriginId"]
                dest = Quotes["OutboundLeg"]["DestinationId"]
                price = Quotes["MinPrice"]

                # return trip
                if self.trip_type == "return":
                    # Print trip info
                    print(outdate.strftime("%d-%b %a") + " - " + indate.strftime("%d-%b %a") + " | " + "%s  --> %s"%(self.airports[source],self.airports[dest]) + " | " + "%s GBP" %Quotes["MinPrice"])
                
                # one way trip
                else:
                    # Print trip info
                    print(outdate.strftime("%d-%b %a") + " | " + "%s  --> %s"%(self.airports[source],self.airports[dest]) + " | " + "%s GBP" %Quotes["MinPrice"])

