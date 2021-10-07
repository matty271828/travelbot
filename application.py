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

sql = "DELETE FROM best_flights"
clear_best_flights = run_sql(sql)

#sql = "DELETE FROM place_info"
#clear_place_info = run_sql(sql)

#sql = "DELETE FROM countries_continents"
#clear_place_info = run_sql(sql)

search_30dayoutward(source_array, destination_array, source_begin_date, source_end_date)

print("\nBenchmark Stats :")
time_in_programme = time.time()-function_start
print("Time spent in program: %f seconds"%(time_in_programme))

# Send email with status update for application
#sender = "mattycodeupdates@gmail.com"
#receivers = ["macleanmatty@gmail.com"]
#body_of_email = (f"travelbot script completed in: {time_in_programme}s")

#msg = MIMEText(body_of_email, "html")
#msg["Subject"] = "Travelbot status update"
#msg["From"] = sender
#msg["To"] = ",".join(receivers)

# Get email key
#codeupdates_key = os.environ.get('email_key')

#s = smtplib.SMTP_SSL(host = "smtp.gmail.com", port = 587)
#s.login(user = "mattycodeupdates@gmail.com", password = codeupdates_key)
#s.sendmail(sender, receivers, msg.as_string())
#s.quit()