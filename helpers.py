import requests, datetime, json

class findingCheapestFlights:
    
    def __init__(self, originCountry = "UK", currency = "GBP", locale = "en", rootURL="https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com"):
        self.currency = currency
        self.locale =  locale
        self.rootURL = rootURL
        self.originCountry = originCountry

    def setHeaders(self, headers):
        self.headers =  headers

    def browseQuotes(self, source, destination, date):
        quoteRequestPath = "/apiservices/browsequotes/v1.0/"
        browseQuotesURL = self.rootURL + quoteRequestPath + self.originCountry + "/" + self.currency + "/" + self.locale + "/" + source + "/" + destination + "/" + date.strftime("%Y-%m-%d")
        response = requests.request("GET", url = browseQuotesURL, headers = self.headers)
        resultJSON = json.loads(response.text)
        return resultJSON
