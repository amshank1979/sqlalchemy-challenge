# Import the dependencies.
from flask import Flask, jsonify
import datetime as dt
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base


# Create an engine for the database
db_path = 'chinook.sqlite'
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect the database
Base = automap_base()
Base.prepare(autoload_with=engine)

# Define references to the reflected tables
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create the Flask app
app = Flask(__name__)
one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
@app.route("/")
def home():
    return (
        f"Welcome to the Chinook API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()
    session.close() 
   # Convert the query results to a dictionary with date as the key and prcp as the value
    precipitation_data = {}
    for date, prcp in results:
        precipitation_data[date] = prcp
        
    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def stations():
    # Query the database for station data
    session = Session(engine)
    
    # Replace 'Stations' with the actual class name for your stations table
    results = session.query(Station.station).all()
    
    session.close()
    
    # Convert the query results to a list of station names
    station_list = [result[0] for result in results]
    
    return jsonify(station_list)   

@app.route("/api/v1.0/tobs")
def tobs():
 # Query the database for temperature observations
    session = Session(engine)
    
    # Replace 'Measurement' and 'Station' with your actual class names
    most_active_station = (
        session.query(Measurement.station)
        .group_by(Measurement.station)
        .order_by(func.count().desc())
        .first()
    )
    
    
    
    # Replace 'Measurement' with your actual class name
    results = (
        session.query(Measurement.date, Measurement.tobs)
        .filter(Measurement.station == most_active_station[0])
        .filter(Measurement.date >= one_year_ago)
        .all()
    )
    
    session.close()
    
    # Convert the query results to a list of dictionaries
    temperature_data = []
    for date, tobs in results:
        temperature_data.append({"date": date, "tobs": tobs})
    
    return jsonify(temperature_data)   

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temperature_range(start, end=None):
  # Query the database for temperature statistics
    session = Session(engine)
    
    # Replace 'Measurement' with your actual class name
    if end:
        results = (
            session.query(
                func.min(Measurement.tobs),
                func.avg(Measurement.tobs),
                func.max(Measurement.tobs)
            )
            .filter(Measurement.date >= start)
            .filter(Measurement.date <= end)
            .all()
        )
    else:
        results = (
            session.query(
                func.min(Measurement.tobs),
                func.avg(Measurement.tobs),
                func.max(Measurement.tobs)
            )
            .filter(Measurement.date >= start)
            .all()
        )
    
    session.close()
    
    # Convert the query results to a dictionary
    temperature_stats = {
        "min_temperature": results[0][0],
        "avg_temperature": results[0][1],
        "max_temperature": results[0][2]
    }
    
    return jsonify(temperature_stats)

# Add code to run the app if executed as a standalone script
if __name__ == "__main__":
    app.run(debug=True)


