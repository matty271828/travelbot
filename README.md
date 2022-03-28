# Travelbot Backend

### Project Background

The files in this repository act as the backend for my TravelBot web application. I developed this application to search for cheap flights daily and output the results to a web-page. A separate repository contains the files for the application front end and can be found here ():

One may ask why bother? Don't services such as Skyscanner, Expedia or Kayak already fulfill this function? Yes they do. However with the power of programing we are able to do more!

### Use of Skyscanner API

After discovering Skyscanner had a handy API to output 10s of thousands of their cheapest journeys, I decided to use this to explore all possible permutations of UK airports -> Global airports, and within those the various dates for outward and return journeys for each aiport origin and destination pair. This is something that would take many hours of browsing the web to do manually.

The core code includes the API contact and interpration of the JSON response, as well as use of threading in python to speed up run time. 

I then took a different route than the tutorial in the implementation of a trip planner. I have developed my own algorithm and automated running of the programme to search for cheap flights thorughout the year and send automated emails with good offers. (Please note development is still ongoing as of time of writing of this document).

### Database

### Heroku hosting

### Screenshots of Web Application

![travelbot_ Home](https://user-images.githubusercontent.com/65253959/160440885-69161e01-78ec-421e-be83-269159eec961.jpeg)

![travelbot_ Browse](https://user-images.githubusercontent.com/65253959/160440264-7ba7ea7e-8bd5-4802-babd-06525260b972.jpeg)

### Skyscanner Depreciation 

Unfortunately, since developing this project, Skyscanner have depreciated the usage of their API to non-commerical customers. Hence this web application is no longer live. 
