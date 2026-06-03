Disease Case Log
A Flask web application for logging, reviewing, and visualizing sample disease case records.

Disease Case Log includes a case dashboard, CRUD forms, CSV export, an interactive map, and a local AI-style outbreak analyst that ranks outbreak risk and generates case note drafts.

Project Status
This is a demo/student project built with sample public-health-style data. It is intended for learning Flask, routing, templates, forms, API endpoints, and front-end interactivity.

Features
Dashboard summary metrics for total cases, disease types, affected locations, and critical outbreaks
Outbreak spotlight carousel for recent case records
Searchable and severity-filtered case records table
Add, edit, and delete case records
Export case records as a CSV file
Interactive Leaflet map with sample disease markers
AI-style outbreak analyst with:
auto-generated summary report
outbreak risk prediction
trend detection
generated case note drafts
Tech Stack
Python
Flask
Jinja
HTML
CSS
JavaScript
Leaflet.js
OpenStreetMap tiles
Quick Start
1. Clone the repository
git clone <your-repository-url>
cd DiseaseCaseLog
2. Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate
On Windows:

python -m venv .venv
.venv\Scripts\activate
3. Install dependencies
python3 -m pip install flask
4. Run the app
python3 app.py
Then open:

http://127.0.0.1:5000
You can also run the app with the Flask CLI:

flask --app app run --debug
Pages and Routes
Route	Description
/	Dashboard with summary metrics, outbreak spotlight, and case records
/add	Add a new case record
/edit/<case_id>	Edit an existing case record
/delete/<case_id>	Delete a case record with a POST request
/export	Download case records as disease_case_log.csv
/map	View sample disease locations on a Leaflet map
/api/get_cases_data/	JSON endpoint used by the map
/ai_outbreak_analyst	View generated outbreak analysis and risk predictions
/ai_analysis	JSON endpoint for generated case note drafts
Project Structure
DiseaseCaseLog/
|-- app.py
|-- static/
|   |-- css/
|   |   `-- styles.css
|   `-- js/
|       |-- ai_outbreak_analyst.js
|       |-- case_records.js
|       |-- map_view_api.js
|       `-- outbreak_spotlight.js
`-- templates/
    |-- ai_outbreak_analyst.html
    |-- case_form.html
    |-- index.html
    |-- map_view.html
    `-- styles.html
How the Data Works
The application currently uses in-memory sample data stored in app.py.

CASE_RECORDS powers the dashboard, case form pages, CSV export, and AI-style analyst.
CASE_DATA powers the map markers.
Because the data is stored in Python lists, records added, edited, or deleted through the UI are not permanently saved. The data resets when the Flask server restarts.

AI-Style Analyst Note
The outbreak analyst does not call an external AI API. It uses local rule-based logic to calculate risk scores from:

severity level
case count
report recency
It also generates note drafts using templates based on the selected case record and note style.

Development Notes
The app uses Flask's built-in development server.
SECRET_KEY is currently set to a development value.
The map page loads Leaflet from a CDN and map tiles from OpenStreetMap.
The sample data is for demonstration only and should not be treated as real public health data.
Future Improvements
Add a requirements.txt file.
Save case records with SQLite or another database.
Connect dashboard records and map markers to the same data source.
Add user authentication.
Add automated tests for forms, CSV export, and API endpoints.
Deploy the app to a hosting platform such as Render, Railway, or PythonAnywhere.
