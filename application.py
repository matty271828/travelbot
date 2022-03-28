import requests
import json
import os
import time, datetime
import pandas as pd
import smtplib,ssl
from email.mime.text import MIMEText
import time, datetime
from datetime import timedelta, date

from functions import process_places, search_30dayreturn, search_oneway, search_30dayoutward, search_specificreturn
from run_sql import run_sql

# Airports where we can fly from
source_array = {"UK-sky"} 
# Our destination airports
destination_array = {"US-sky","everywhere"}

# Dates
begin_date = date.today() + timedelta(days=1)
end_date = begin_date + timedelta(days=200)

source_begin_date = pd.to_datetime(begin_date)
source_end_date =  pd.to_datetime(end_date)

# -----------------------------------------------------------------------

# time request
total_compute_time = 0.0
total_request_time = 0.0

# Start timer
function_start = time.time()

# Clear all tables
sql = "DELETE FROM return_flights"
clear_return_flights = run_sql(sql)

sql = "DELETE FROM onewayflights"
clear_onewayflights = run_sql(sql)

#sql = "DELETE FROM best_flights"
#clear_best_flights = run_sql(sql)

#sql = "DELETE FROM place_info"
#clear_place_info = run_sql(sql)

#sql = "DELETE FROM countries_continents"
#clear_place_info = run_sql(sql)

# -------------------- Dummy data inserted as Skyscanner API has now been depriciated --------
# populate database with dummy date due to API depreciation
sql = f"INSERT INTO best_flights (id, origin_id, source, destination_id, dest, country, continent, price, outdate, indate) VALUES (1, 'LPL', 'Liverpool John Lennon Airport', 'CDG', 'Paris - Charles De Gaulle', 'France', 'EU', 15, '2022-07-07', '2022-07-12')"
populate_dummy_data = run_sql(sql)

# -----------------------------------------------------------
# Function call to conduct search for best flights using skyscanner API
#search_30dayoutward(source_array, destination_array, source_begin_date, source_end_date)

print("\nBenchmark Stats :")
time_in_programme = time.time()-function_start
print("Time spent in program: %f seconds"%(time_in_programme))