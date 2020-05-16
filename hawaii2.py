import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from datetime import datetime
from flask import Flask, jsonify, request


engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#Flask Setup
app = Flask(__name__)

#Flask Routes

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start_end" )
        
@app.route("/api/v1.0/precipitation")
def precip():
     # Create our session (link) from Python to the DB
    session = Session(engine)
         # Find the date of the last day recorded in the data
    last_day = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    #Convert last day to an object so I can find a year previous
    ld_object = datetime.strptime(last_day[0], '%Y-%m-%d') 

    # Calculate the date 1 year ago from the last data point in the database
    year_ago = ld_object-dt.timedelta(days = 366)  

    results = session.query(Measurement.date,Measurement.prcp).filter(func.strftime("%Y-%m-%d",Measurement.date) >= year_ago ).all()
    
    session.close()

    # Create a dictionary from the row data and append to a list of all_passengers
    date_precip_dict = {}
    for date, prcp in results:
        date_precip_dict[date]=prcp
      

    return jsonify(date_precip_dict)       
           
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    results = session.query(Station).distinct(Station.station).group_by(Station.station).count()
    
    session.close()
    
    station = list(np.ravel(results))
    
    return station
        
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Find the date of the last day recorded in the data
    last_day = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    #Convert last day to an object so I can find a year previous
    ld_object = datetime.strptime(last_day[0], '%Y-%m-%d') 

    # Calculate the date 1 year ago from the last data point in the database
    year_ago = ld_object-dt.timedelta(days = 366)   

    results = session.query(Measurement.tobs).filter_by(station= 'USC00519281').\
        filter(func.strftime("%Y-%m-%d",Measurement.date) >= year_ago).all()
    
    session.close()
    
    tobs = list(np.ravel(results))
    
    return jsonify(tobs)  
        
@app.route("/api/v1.0/start")
def col_date():
    return """
            <html>
            <body>

            <h1>Choose a date to start your vacation.</h1>

            <form action="/action_page.php">
              <label for="st_day">Start Date:</label>
              <input type="date" id="st_day" name="st_day">
              <input type="submit" value='Continue'>
            </form>

            <p><strong>Note:</strong> type="date" is not supported in Safari or Internet Explorer 11 (or earlier).</p>

            </body>
            </html>
           """
@app.route("/action_page.php")
def temp_out():    # Create our session (link) from Python to the DB
    st_month = request.args['month']
    st_day = request.args['day']

    if int(st_month) < 8:
        year = 2017
    elif int(st_month) == 8:
        if int(st_day) <= 23:
            year = 2017
        else:
            year = 2016
    else:
        year = 2016
    beyond_date = f"{year}-{st_month}-{st_day}"
    bd_object = datetime.strptime(beyond_date, '%Y-%m-%d')
    session = Session(engine)
    result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(func.strftime("%Y-%m-%d",Measurement.date) >= bd_object).all()
    session.close()
    
    start_t = list(np.ravel(result))

    return """
        <html><body>
             <h2>Avg Temp: {0}</h2><br>
             <h2>Max Temp: {1}</h2><br>
             <h2>Min Temp: {2}</h2>
        </body></html>
        """.format(start_t[1],start_t[2],start_t[0])

@app.route("/api/v1.0/start_end")
def col_dates():
    return """
         <html><body>
             <h2>Please give me details of your vacation start date and end date.</h2>
             <form action="/range_temp_out">
                 Start month? <input type='number' name='start_month'><br>
                 Start day? <input type='number' name='start_day'><br>
                 End month? <input type='number' name='end_month'><br>
                 End day? <input type='number' name='end_day'><br>
                 <input type='submit' value='Continue'>
             </form>
         </body></html>
         """
@app.route("/range_temp_out")
def range_temp_out():    # Create our session (link) from Python to the DB
    st_month = request.args['start_month']
    st_day = request.args['start_day']
    en_month = request.args['end_month']
    en_day = request.args['end_day']

    if int(st_month) < 8:
        year = 2017
    elif int(st_month) == 8:
        if int(st_day) <= 23:
            year = 2017
        else:
            year = 2016
    else:
        year = 2016
    start_date = f'{year}-{st_month}-{st_day}'
    sd_object = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = f'{year}-{en_month}-{en_day}'
    ed_object = datetime.strptime(end_date, '%Y-%m-%d')
    start_date = '2017-3-10'
    end_date = '2017-3-20' 
    session = Session(engine)
    result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    session.close()
    
    range_t = list(np.ravel(result))
    #return jsonify(range_t)
    return """
        <html><body>
            <h2>Great choice to vacation between {3}-{4} and {5}-{6}. You can expect the following weather.</h2><br>
            <p>{7}, {8} </p>
            <h3>Avg Temp: {0}</h3><br>
            <h3>Max Temp: {1}</h3><br>
            <h3>Min Temp: {2}</h3>
        </body></html>
        """.format(range_t[1],range_t[2],range_t[0],st_month,st_day,en_month,en_day,start_date,end_date)
        
# @app.route("/api/v1.0/<start>/<end>")
# def start_end():
#     # Create our session (link) from Python to the DB
#     session = Session(engine)
           
#     return:

if __name__ == '__main__':
    app.run(debug=True)