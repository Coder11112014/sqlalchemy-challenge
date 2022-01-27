from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
import numpy as np
import datetime as dt

#Create engine to connect with database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

#Reflect an existing database into a new model
Base = automap_base()

#Reflect the tables
Base.prepare(engine, reflect=True)

#Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station


session = Session(engine)

# find the last date in the database
last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

# Calculate the date 1 year ago from the last data point in the database
query_date = dt.date(2017,8,23) - dt.timedelta(days=365)

session.close()


# Flask
app = Flask(__name__)

# Create routes
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"<h1>Welcome to Hawaii climate API!</h1>"
        f"<h2>List of routes:</h2>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start/end<br/>"

        
        f"<ol><li><a href=http://127.0.0.1:5000/api/v1.0/precipitation>"
        f"JSON list of precipitation amounts by date for the most recent year of data available</a></li><br/><br/>"
        f"<li><a href=http://127.0.0.1:5000/api/v1.0/stations>"
        f"JSON list of weather stations and their details</a></li><br/><br/>"
        f"<li><a href=http://127.0.0.1:5000/api/v1.0/tobs>"
        f"JSON list of the last 12 months of recorded temperatures</a></li><br/><br/>"
        f"<li><a href='/api/v1.0/min_max_avg/2012-01-01/2016-12-31' target='_blank'>/api/v1.0/min_max_avg/2012-01-01/2016-12-31</a>"
    )
       
    


@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).all()
    session.close()

    precipitation_dict = []
    for row in results:
        date_dict = {}
        date_dict[row[0]] = row[1]
        precipitation_dict.append(date_dict)

    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.station,Station.name,Station.latitude, Station.longitude, Station.elevation).all()
    session.close()
    station_list = []

    for row in results:
        station_dict = {}
        station_dict["station"] = row[0]
        station_dict["name"] = row[1]
        station_dict["latitude"] = row[2]
        station_dict["longitude"] = row[3]
        station_dict["elevation"] = row[4]
        station_list.append(station_dict)
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine) 
    most_active_station = session.query(Measurement.station).group_by(Measurement.station).order_by(func.count().desc()).first()
    (most_active_station_id, ) = most_active_station
    results = session.query(Measurement.tobs, Measurement.date ).filter( Measurement.station == most_active_station_id).filter(Measurement.date >= "2016-08-23").filter(Measurement.date <= "2017-08-23").all()
 
    session.close()

    tobs_list = []
    for result in results:
       tobs_dict = {}
       tobs_dict["date"] = result[1]
       tobs_dict["temprature"] = result[0]
       tobs_list.append(tobs_dict)

    return jsonify(tobs_list)



@app.route("/api/v1.0/min_max_avg/<start>/<end>")
def start_end(start, end):
    # create session link
    session = Session(engine)

    start_dt = dt.datetime.strptime(start, '%Y-%m-%d')
    end_dt = dt.datetime.strptime(end, "%Y-%m-%d")

   
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_dt).filter(Measurement.date <= end_dt)

    session.close()

    # Create a list to hold results
    date_list = []
    for row in results:
        date_dict = {}
        date_dict["StartDate"] = start_dt
        date_dict["EndDate"] = end_dt
        date_dict["TMIN"] = row[0]
        date_dict["TAVG"] = row[1]
        date_dict["TMAX"] = row[2]
        date_list.append(date_dict)

    # jsonify the result
    return jsonify(date_list)



if __name__ == '__main__':
    app.run(debug=True)