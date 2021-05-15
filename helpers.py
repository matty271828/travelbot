import requests, datetime, json

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
        
    def browsereturnQuotes(self, source, destination, outdate, indate):
        self.trip_type = "return"
        quoteRequestPath = "/apiservices/browsequotes/v1.0/"
        browsereturnQuotesURL = self.rootURL + quoteRequestPath + self.originCountry + "/" + self.currency + "/" + self.locale + "/" + source + "/" + destination + "/" + outdate.strftime("%Y-%m-%d") + "/" + indate.strftime("%Y-%m-%d")
        # Use the same session to request again and again
        response = self.session.get(browsereturnQuotesURL)
        resultJSON = json.loads(response.text)
        self.printResult(resultJSON, outdate, indate)
        
    # A bit more elegant print
    def printResult(self, resultJSON, outdate, indate):
        if("Quotes" in resultJSON):
            for Places in resultJSON["Places"]:
                self.airports[Places["PlaceId"]] = Places["Name"] 
            for Quotes in resultJSON["Quotes"]:
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
