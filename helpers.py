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
        
    def browseonewayQuotes(self, source, destination, date):
        quoteRequestPath = "/apiservices/browsequotes/v1.0/"
        browseQuotesURL = self.rootURL + quoteRequestPath + self.originCountry + "/" + self.currency + "/" + self.locale + "/" + source + "/" + destination + "/" + date.strftime("%Y-%m-%d")
        # Use the same session to request again and again
        response = self.session.get(browseQuotesURL)
        resultJSON = json.loads(response.text)
        self.printResult(resultJSON,date)
        
    # A bit more elegant print
    def printResult(self, resultJSON,date):
        if("Quotes" in resultJSON):
            for Places in resultJSON["Places"]:
                self.airports[Places["PlaceId"]] = Places["Name"] 
            for Quotes in resultJSON["Quotes"]:
                source = Quotes["OutboundLeg"]["OriginId"]
                dest = Quotes["OutboundLeg"]["DestinationId"]
                print(date.strftime("%d-%b %a") + " | " + "%s  --> %s"%(self.airports[source],self.airports[dest]) + " | " + "%s GBP" %Quotes["MinPrice"])
