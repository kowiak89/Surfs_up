import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Create the engine 
engine = create_engine("sqlite:///hawaii.sqlite")

# Reflect the database into classes (columns)
Base = automap_base()
Base.prepare(engine, reflect=True)

# Create references to the database
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session
session = Session(engine)

# Create the flask app
app = Flask(__name__)

# Create the root route
@app.route("/")
def welcome():
    return(
    '''
    Welcome to the Climate Analysis API!
    Available Routes:
    /api/v1.0/precipitation
    /api/v1.0/stations
    /api/v1.0/tobs
    /api/v1.0/temp/start/end
    ''')

# Create the other routes
# Precipitation:
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Get the date for the previous year
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query the database for the precipitation data
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year).all() # Get all of the dates and precipitation amnts for the prev year
    
    # create a dictionary to hold the date and precipitation amount
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip) # jsonify precip so it can be uploaded to the internet easily

# Stations:
@app.route("/api/v1.0/stations")
def stations():
    # query the database for the station data
    results = session.query(Station.station).all()
    
    # unravel results and then convert it into a list - not sure why we need to unravel
    stations = list(np.ravel(results))

    return jsonify(stations=stations)

# Temperature
@app.route("/api/v1.0/tobs")
def temp_monthly():
    # Get the date from 1 year ago
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Get the weather data from the previous year
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_year).all()
    
    # unravel and convert to list
    temps = list(np.ravel(results))

    return jsonify(temps=temps)

# Statistics route
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
# we need start date and end date parameters cause the stats are time sensitive
def stats(start=None, end=None):
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
        temps = list(np.ravel(results))
        return jsonify(temps)

    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    temps = list(np.ravel(results))
    return jsonify(temps)