import requests, datetime, json

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
        
    def setHeaders(self, headers):
        self.headers =  headers
        self.createSession()

    # Create a session
    def createSession(self):
        self.session = requests.Session() 
        self.session.headers.update(self.headers)
        return self.session
        
    def browseonewayQuotes(self, source, destination, outdate):
        self.trip_type = "oneway"
        quoteRequestPath = "/apiservices/browsequotes/v1.0/"
        browseonewayQuotesURL = self.rootURL + quoteRequestPath + self.originCountry + "/" + self.currency + "/" + self.locale + "/" + source + "/" + destination + "/" + outdate.strftime("%Y-%m-%d")
        # Use the same session to request again and again
        response = self.session.get(browseonewayQuotesURL)
        resultJSON = json.loads(response.text)
        self.printResult(resultJSON, outdate, None)
        
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

        self.printResult(resultJSON, outdate, indate, max_budget)
        
    # A bit more elegant print
    def printResult(self, resultJSON, outdate, indate, max_budget):
        # Check for response
        if("Quotes" in resultJSON):
            for Places in resultJSON["Places"]:
                self.airports[Places["PlaceId"]] = Places["Name"] 
            for Quotes in resultJSON["Quotes"]:
                # Check flight within budget
                if (max_budget == None):
                    pass
                elif (Quotes["MinPrice"] > max_budget):
                    break

                # return trip
                if self.trip_type == "return":
                    source = Quotes["OutboundLeg"]["OriginId"]
                    dest = Quotes["OutboundLeg"]["DestinationId"]
                    print(outdate.strftime("%d-%b %a") + " - " + indate.strftime("%d-%b %a") + " | " + "%s  --> %s"%(self.airports[source],self.airports[dest]) + " | " + "%s GBP" %Quotes["MinPrice"])
                # one way trip
                else:
                    source = Quotes["OutboundLeg"]["OriginId"]
                    dest = Quotes["OutboundLeg"]["DestinationId"]
                    print(outdate.strftime("%d-%b %a") + " | " + "%s  --> %s"%(self.airports[source],self.airports[dest]) + " | " + "%s GBP" %Quotes["MinPrice"])
