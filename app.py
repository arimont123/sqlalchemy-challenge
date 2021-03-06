import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify

#Database setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

#Reflect an existing database into a new model
Base = automap_base()
#Reflect the tables
Base.prepare(engine,reflect=True)
#Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#Flask setup
app = Flask(__name__)

# Flask Routes
@app.route("/")
def welcome():
    return(
        f"Welcome to the Home Page.<br/>"
        f"Available Routes: <br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

#Returns a dictionary of date and preciptation amount for the last year of data in Hawaii
from collections import defaultdict 
@app.route("/api/v1.0/precipitation")
def precipitation():
    #Create session link from python to the DB
    session = Session(engine)
    #Query results
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results= session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()
    session.close()
    #Create dictionary of date (key) and prcp (value)
    date_prcp_dict = defaultdict(list)
    for key, val in results:
        date_prcp_dict[key].append(val)
        
    return jsonify(date_prcp_dict)  

#Returns a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    #Create session
    session = Session(engine)
    #Query a list of stations from the dataset
    station_list = session.query(Measurement.station).group_by(Measurement.station).all()
    session.close()
    station_list_dict = {"List of temperature stations in Hawaii": station_list }
    return jsonify(station_list_dict)

#Query the dates and temperature observations of the most active station for the last year of data.
@app.route("/api/v1.0/tobs")
def tobs():
    #Create session
    session = Session(engine) 
    #Find date for the previous year of data
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    #Query date and temperature for the most active station and for last year of data
    tobs_results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date >= one_year_ago).all()
    session.close()    
    #Return a JSON list of temperature observations (TOBS) for the previous year
    station_dict = {"Date and Temparture Observations for station USC00519281 From 2016-8-23 to 2017-8-23": tobs_results}
    return jsonify(station_dict)

#Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range
from datetime import datetime
@app.route("/api/v1.0/<start>")
def temp_data(start):
#When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.
    session = Session(engine)
    #Correct format for datetime 
    corrected = start.replace("-", "")
    start_date = datetime.strptime(corrected, '%Y%m%d').strftime('%Y-%m-%d') 
    
    #Query data
    max_temp = session.query(func.max(Measurement.tobs)).filter(Measurement.date >= start_date).all()
    min_temp = session.query(func.min(Measurement.tobs)).filter(Measurement.date >= start_date).all()
    avg_temp = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= start_date).all()
    
    #Create dictionary
    temp_dict = {"Start Date": start_date, "Max Temp": max_temp, "Min Temp": min_temp,"Average Temp": avg_temp}
    
    return jsonify(temp_dict)

#When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.
@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):
    session = Session(engine)
    corrected_start = start.replace("-", "")
    start_date = datetime.strptime(corrected_start, '%Y%m%d').strftime('%Y-%m-%d') 
    corrected_end = end.replace("-", "")
    end_date = datetime.strptime(corrected_end,'%Y%m%d').strftime('%Y-%m-%d') 
    
    max_temp = session.query(func.max(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    min_temp = session.query(func.min(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    avg_temp = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    #Create dictionary
    temp_dict = {"Start Date": start_date, "End Date": end_date, "Max Temp": max_temp, "Min Temp": min_temp,"Average Temp": avg_temp}
    
    return jsonify(temp_dict)
       
    
if __name__ == '__main__':
    app.run(debug=False)        
        
        
        
