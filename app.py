import numpy as np
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
Base.prepare(engine, reflect=True)

# Save references to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt<br/>"
        f"/api/v1.0/&lt;start&gt/&lt;end&gt<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query the data
    results =   session.query(Measurement.date, Measurement.prcp).\
                order_by(Measurement.date).all()

    # Create list of dictionaries
    
    prcp_date_list = []

    for date, prcp in results:
        new_dict = {}
        new_dict[date] = prcp
        prcp_date_list.append(new_dict)

    session.close()

    return jsonify(prcp_date_list)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    """Return a json list of stations from the dataset."""
    
    stations = {}

    # Query all stations
    results = session.query(Station.station, Station.name).all()
    for station, name in results:
        stations[station] = name

    session.close()
 
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    """Return a json list of Temperature Observations (tobs) for the previous year"""
    
    # Get the last date contained in the dataset and date from one year ago
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    one_year_ago = (dt.datetime.strptime(last_date[0],'%Y-%m-%d') \
                    - dt.timedelta(days=365)).strftime('%Y-%m-%d')

    # Query for the dates and temperature values
    results =   session.query(Measurement.date, Measurement.tobs).\
                filter(Measurement.date >= one_year_ago).\
                order_by(Measurement.date).all()

    # Create list of dictionaries
    tobs_date_list = []

    for date, tobs in results:
        new_dict = {}
        new_dict[date] = tobs
        tobs_date_list.append(new_dict)

    session.close()

    return jsonify(tobs_date_list)
    
@app.route("/api/v1.0/<start>")
def startonwards(start):
    
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a json of the minimum average and the max temperature for a given start date"""
    
    # take any date and convert to yyyy-mm-dd format for the query
    start_dt = dt.datetime.strptime(start, '%Y-%m-%d')

    # query data for the start date value
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_dt).all()

    session.close()

    # Create a list to hold results
    t_list = []
    for result in results:
        r = {}
        r["StartDate"] = start_dt
        r["TMIN"] = result[0]
        r["TAVG"] = result[1]
        r["TMAX"] = result[2]
        t_list.append(r)

    # jsonify the result
    return jsonify(t_list)
    

@app.route("/api/v1.0/temp/<start>/<end>")
def period(start, end):
    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    """Return a json of the minimum average and the max temperature for a given period"""
    
    # take start and end dates and convert to yyyy-mm-dd format for the query
    start_dt = dt.datetime.strptime(start, '%Y-%m-%d')
    end_dt = dt.datetime.strptime(end, "%Y-%m-%d")

    # query data for the start date value
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start_dt).\
                filter(Measurement.date <= end_dt)

    session.close()

    # Create a list to hold results
    return_list = []
    for result in results:
        r = {}
        r["StartDate"] = start_dt
        r["EndDate"] = end_dt
        r["TMIN"] = result[0]
        r["TAVG"] = result[1]
        r["TMAX"] = result[2]
        return_list.append(r)

    # jsonify the result
    return jsonify(return_list)

if __name__ == '__main__':
    app.run(debug=True)