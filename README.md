# location-finder
Python flask web application for selecting different locations (i.e., counties) in United States based on multiple factors related to population, earnings, age, housing, education, rent, employment, health and physical activity. 

The different factors are standardized using linear transformation and then aggregated into a suitability index by weighting each standardized factor with user-specified importance weights. The suitability indices for each county are then ranked from most suitable to least suitable and displayed on a map.

Web Application Framework: Python Flask <br>
Backend: Python (NumPy, Pandas), SQLite <br>
Frontend: HTML, CSS, JavaScript, jQuery, Ajax, Bootstrap, D3

<br><br>
![alt tag](https://raw.githubusercontent.com/b-ghimire/location-finder/master/flask_app/static/img/location_finder.png)
