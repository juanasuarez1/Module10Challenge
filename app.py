# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement

station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes,
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/percipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/percipitation")
def percipitation():
       # Create our session (link) from Python to the DB
    session = Session(engine)

    """Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value."""
    # Query the last 12 months
    one_year_ago = dt.date(2017,8,23)-dt.timedelta(days=365)
    results = session.query(measurement.date, measurement.prcp).filter(measurement.date >= one_year_ago).all()

    session.close()

    # Return results as a dictionary 
    dict_results = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        dict_results.append(prcp_dict)

    return jsonify(dict_results)

# JSON list of station names, GOOD
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    # """Return a JSON list of stations from the dataset."""
    # Query all station names
    results = session.query(station.name).all()

    session.close()

    # Convert list of tuples into normal list
    all_names = list(np.ravel(results))

    return jsonify(all_names)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    # Query the dates and temperature observations of the most-active station for the previous year of data.
    one_year_ago = dt.date(2017,8,23)-dt.timedelta(days=365)
    tobs_data = session.query(measurement.date, measurement.tobs).filter(measurement.station=='USC00519281').filter(measurement.date >= one_year_ago).all()

    session.close()

    # Convert list of tuples into normal list
    all_tobs = list(np.ravel(tobs_data))

    # Return a JSON list of temperature observations for the previous year.
    return jsonify(all_tobs)

@app.route("/api/v1.0/<start>")
def start(start):

    # Use try and except statement to deal with errors
    try:
        start_date = dt.datetime.strptime(start, "%m%d%Y")
    except ValueError:
        return "Error! Please use mmddyyyy format."

    # query min, avg, and max for anything after start date
    start_temps = session.query(func.min(measurement.tobs),func.avg(measurement.tobs),func.max(measurement.tobs)).filter(measurement.date >= start_date).all()

    session.close()

    start_data = list(np.ravel(start_temps))

    # JSONIFY the results
    return jsonify(start_data)

@app.route("/api/v1.0/<start>/<end>")
def start_and_end(start, end):

    # Use try and except statement to deal with errors
    try:
        start_date = dt.datetime.strptime(start, "%m%d%Y")
        end_date = dt.datetime.strptime(end, "%m%d%Y")
    except ValueError:
        return "Error! Please use mmddyyyy format."
    
    # query min, avg, and max for anything between the start and end date
    start_and_end_temps = session.query(func.min(measurement.tobs),func.avg(measurement.tobs),func.max(measurement.tobs)).filter(measurement.date >= start_date).filter(measurement.date <= end_date).all()
    
    session.close()

    start_and_end_data = list(np.ravel(start_and_end_temps))

    # JSONIFY the results
    return jsonify(start_and_end_data)


if __name__ == '__main__':
    app.run(debug=True)