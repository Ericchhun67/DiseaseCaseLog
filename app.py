"""
Disease Case Log Application
"""


import csv
from collections import defaultdict
from datetime import date, datetime
from io import StringIO

from flask import (
    Flask,
    Response,
    abort,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key'

SEVERITY_LEVELS = ('Low', 'Moderate', 'High', 'Critical')
SEVERITY_RISK_WEIGHTS = {
    'Low': 10,
    'Moderate': 22,
    'High': 34,
    'Critical': 45,
}

CASE_RECORDS = [
    {
        'id': 1,
        'disease_name': 'Flu',
        'severity': 'Low',
        'location': 'Seattle, WA',
        'case_count': 875,
        'date_reported': date(2026, 4, 28),
        'notes': 'Mild season. Most cases self-reported.',
    },
    {
        'id': 2,
        'disease_name': 'COVID-19',
        'severity': 'Critical',
        'location': 'Phoenix, AZ',
        'case_count': 512,
        'date_reported': date(2026, 4, 26),
        'notes': 'ICU capacity at 87%. Emergency protocols activated.',
    },
    {
        'id': 3,
        'disease_name': 'Food Poisoning',
        'severity': 'Moderate',
        'location': 'Houston, TX',
        'case_count': 58,
        'date_reported': date(2026, 4, 25),
        'notes': 'Suspected source: local catering event.',
    },
    {
        'id': 4,
        'disease_name': 'Flu',
        'severity': 'Moderate',
        'location': 'Los Angeles, CA',
        'case_count': 1204,
        'date_reported': date(2026, 4, 22),
        'notes': 'Seasonal influenza A strain. Vaccination clinics expanded.',
    },
    {
        'id': 5,
        'disease_name': 'COVID-19',
        'severity': 'High',
        'location': 'New York, NY',
        'case_count': 342,
        'date_reported': date(2026, 4, 20),
        'notes': 'Spike observed in Brooklyn and Queens boroughs.',
    },
    {
        'id': 6,
        'disease_name': 'Measles',
        'severity': 'High',
        'location': 'Chicago, IL',
        'case_count': 17,
        'date_reported': date(2026, 4, 18),
        'notes': 'Cluster linked to a school. Quarantine notices issued.',
    },
    {
        'id': 7,
        'disease_name': 'Dengue',
        'severity': 'High',
        'location': 'Miami, FL',
        'case_count': 29,
        'date_reported': date(2026, 4, 15),
        'notes': 'Vector control spraying initiated.',
    },
    {
        'id': 8,
        'disease_name': 'Hepatitis A',
        'severity': 'Moderate',
        'location': 'Denver, CO',
        'case_count': 12,
        'date_reported': date(2026, 4, 10),
        'notes': 'Linked to contaminated produce at local market.',
    }, 
]

CASE_DATA = [
    {
        'area': 'Los Angeles County',
        'disease': 'Influenza',
        'cases': 42,
        'latitude': 34.0522,
        'longitude': -118.2437,
    },
    {
        'area': 'San Diego County',
        'disease': 'Measles',
        'cases': 18,
        'latitude': 32.7157,
        'longitude': -117.1611,
    },
    {
        'area': 'San Francisco County',
        'disease': 'COVID-19',
        'cases': 27,
        'latitude': 37.7749,
        'longitude': -122.4194,
    },
    {
        'area': 'Sacramento County',
        'disease': 'Norovirus',
        'cases': 15,
        'latitude': 38.5816,
        'longitude': -121.4944,
    },
    {
        'area': 'Fresno County',
        'disease': 'Dengue',
        'cases': 10,
        'latitude': 36.7378,
        'longitude': -119.7871,
    },
    {
        'area': 'Santa Clara County',
        'disease': 'Influenza',
        'cases': 25,
        'latitude': 37.3541,
        'longitude': -121.9552,
    },
    {
        'area': 'Alameda County',
        'disease': 'RSV',
        'cases': 20,
        'latitude': 37.8044,
        'longitude': -122.2711,
    },
    {
        'area': 'Orange County',
        'disease': 'Measles',
        'cases': 30,
        'latitude': 33.7175,
        'longitude': -117.8311,
    },
    {
        'area': 'Riverside County',
        'disease': 'COVID-19',
        'cases': 12,
        'latitude': 33.9533,
        'longitude': -117.3962,
    }
]


def get_case_record(case_id):
    """Find a case record by id."""
    return next(
        (case_record for case_record in CASE_RECORDS if case_record['id'] == case_id),
        None,
    )


def get_next_case_id():
    """Return the next available case id."""
    if not CASE_RECORDS:
        return 1

    return max(case_record['id'] for case_record in CASE_RECORDS) + 1


def read_case_form():
    """Validate submitted form data and return a record-shaped dictionary."""
    errors = {}

    disease_name = request.form.get('disease_name', '').strip()
    severity = request.form.get('severity', '').strip()
    location = request.form.get('location', '').strip()
    case_count_raw = request.form.get('case_count', '').strip()
    date_reported_raw = request.form.get('date_reported', '').strip()
    notes = request.form.get('notes', '').strip()

    if not disease_name:
        errors['disease_name'] = 'Disease name is required.'

    if severity not in SEVERITY_LEVELS:
        errors['severity'] = 'Choose a valid severity.'

    if not location:
        errors['location'] = 'Location is required.'

    try:
        case_count = int(case_count_raw)
        if case_count < 0:
            errors['case_count'] = 'Case count cannot be negative.'
    except ValueError:
        case_count = 0
        errors['case_count'] = 'Case count must be a whole number.'

    try:
        date_reported = datetime.strptime(date_reported_raw, '%Y-%m-%d').date()
    except ValueError:
        date_reported = date.today()
        errors['date_reported'] = 'Use a valid report date.'

    form_data = {
        'disease_name': disease_name,
        'severity': severity,
        'location': location,
        'case_count': case_count,
        'date_reported': date_reported,
        'notes': notes,
    }

    return form_data, errors


def calculate_risk_prediction(case_record, max_case_count, latest_report_date):
    """Create a local AI-style risk prediction for a case record."""
    severity_score = SEVERITY_RISK_WEIGHTS.get(case_record['severity'], 0)
    volume_score = 0

    if max_case_count:
        volume_score = round((case_record['case_count'] / max_case_count) * 35)

    days_since_report = max(
        0,
        (latest_report_date - case_record['date_reported']).days,
    )

    if days_since_report <= 2:
        recency_score = 20
    elif days_since_report <= 7:
        recency_score = 16
    elif days_since_report <= 14:
        recency_score = 12
    elif days_since_report <= 30:
        recency_score = 8
    else:
        recency_score = 4

    risk_score = min(100, severity_score + volume_score + recency_score)

    if risk_score >= 80:
        risk_label = 'High escalation risk'
        recommendation = 'Prioritize immediate review and confirm response capacity.'
    elif risk_score >= 60:
        risk_label = 'Elevated watch'
        recommendation = 'Monitor closely and request a fresh case count update.'
    elif risk_score >= 40:
        risk_label = 'Moderate watch'
        recommendation = 'Keep in the daily review queue and verify notes.'
    else:
        risk_label = 'Stable watch'
        recommendation = 'Continue routine tracking unless new reports arrive.'

    return {
        'score': risk_score,
        'label': risk_label,
        'recommendation': recommendation,
        'explanation': (
            f"{case_record['severity']} severity, "
            f"{case_record['case_count']:,} cases, and "
            f"a report from {days_since_report} day"
            f"{'' if days_since_report == 1 else 's'} before the latest record."
        ),
    }


def generate_case_note(case_record, tone='brief'):
    """Generate a professional note draft for a case record."""
    report_date = case_record['date_reported'].strftime('%B %d, %Y')
    base_note = (
        f"{case_record['disease_name']} activity in {case_record['location']} "
        f"is classified as {case_record['severity'].lower()} severity with "
        f"{case_record['case_count']:,} reported cases as of {report_date}."
    )

    if case_record['severity'] in ('Critical', 'High'):
        next_step = (
            'Recommended follow-up: verify the latest case count, review local '
            'response capacity, and monitor for additional reports.'
        )
    elif case_record['severity'] == 'Moderate':
        next_step = (
            'Recommended follow-up: continue monitoring and update the record if '
            'new cases or exposure details are confirmed.'
        )
    else:
        next_step = (
            'Recommended follow-up: maintain routine surveillance and confirm '
            'whether any new reports change the severity level.'
        )

    existing_note = case_record.get('notes', '').strip()
    if existing_note:
        context = f"Current field notes mention: {existing_note}"
    else:
        context = 'No field notes have been added yet.'

    if tone == 'operations':
        return f"Operations note: {base_note} {context} {next_step}"

    if tone == 'public':
        return (
            f"Public update draft: Health teams are tracking "
            f"{case_record['disease_name']} reports in {case_record['location']}. "
            f"The current log lists {case_record['case_count']:,} cases and a "
            f"{case_record['severity'].lower()} severity level. Updates should be "
            f"shared as new verified information becomes available."
        )

    return f"{base_note} {context} {next_step}"


def build_outbreak_analysis(case_records):
    """Build AI-style outbreak insights from the logged case records."""
    if not case_records:
        return {
            'summary_cards': [],
            'report_lines': ['No case records are available for analysis yet.'],
            'risk_predictions': [],
            'trends': ['Add case records to unlock trend detection.'],
            'initial_note': '',
        }

    max_case_count = max(record['case_count'] for record in case_records)
    latest_report_date = max(record['date_reported'] for record in case_records)
    total_cases = sum(record['case_count'] for record in case_records)
    location_count = len({record['location'] for record in case_records})
    high_priority_count = sum(
        1
        for record in case_records
        if record['severity'] in ('High', 'Critical')
    )

    risk_predictions = []
    for case_record in case_records:
        prediction = calculate_risk_prediction(
            case_record,
            max_case_count,
            latest_report_date,
        )
        risk_predictions.append({
            **case_record,
            'risk_score': prediction['score'],
            'risk_label': prediction['label'],
            'risk_recommendation': prediction['recommendation'],
            'risk_explanation': prediction['explanation'],
        })

    risk_predictions.sort(
        key=lambda record: (
            record['risk_score'],
            record['case_count'],
            record['date_reported'],
        ),
        reverse=True,
    )

    disease_stats = defaultdict(
        lambda: {
            'cases': 0,
            'records': 0,
            'locations': set(),
            'high_priority': 0,
        }
    )

    for case_record in case_records:
        disease = disease_stats[case_record['disease_name']]
        disease['cases'] += case_record['case_count']
        disease['records'] += 1
        disease['locations'].add(case_record['location'])

        if case_record['severity'] in ('High', 'Critical'):
            disease['high_priority'] += 1

    disease_rows = []
    for disease_name, stats in disease_stats.items():
        disease_rows.append({
            'name': disease_name,
            'cases': stats['cases'],
            'records': stats['records'],
            'location_count': len(stats['locations']),
            'high_priority': stats['high_priority'],
        })

    disease_rows.sort(
        key=lambda row: (row['cases'], row['location_count']),
        reverse=True,
    )

    top_disease = disease_rows[0]
    top_prediction = risk_predictions[0]
    recent_records = [
        record for record in case_records
        if (latest_report_date - record['date_reported']).days <= 14
    ]
    multi_location_diseases = [
        row for row in disease_rows
        if row['location_count'] > 1
    ]

    report_lines = [
        (
            f"The log contains {len(case_records)} records across "
            f"{location_count} locations with {total_cases:,} total reported cases."
        ),
        (
            f"{top_disease['name']} has the highest total volume at "
            f"{top_disease['cases']:,} cases across "
            f"{top_disease['location_count']} location"
            f"{'' if top_disease['location_count'] == 1 else 's'}."
        ),
        (
            f"The highest priority prediction is {top_prediction['disease_name']} "
            f"in {top_prediction['location']} with a risk score of "
            f"{top_prediction['risk_score']}."
        ),
    ]

    trends = [
        (
            f"{high_priority_count} record"
            f"{'' if high_priority_count == 1 else 's'} are marked High or Critical, "
            "which should stay near the top of the review queue."
        ),
        (
            f"{len(recent_records)} report"
            f"{'' if len(recent_records) == 1 else 's'} were logged within "
            "14 days of the newest record."
        ),
    ]

    if multi_location_diseases:
        disease_names = ', '.join(row['name'] for row in multi_location_diseases)
        trends.append(
            f"Multi-location activity detected for: {disease_names}."
        )
    else:
        trends.append('No disease currently appears in more than one location.')

    trends.append(
        (
            f"{top_prediction['disease_name']} in {top_prediction['location']} "
            f"is the strongest escalation signal because it combines "
            f"{top_prediction['risk_explanation']}"
        )
    )

    return {
        'summary_cards': [
            {
                'label': 'Highest Risk',
                'value': f"{top_prediction['risk_score']}/100",
                'detail': f"{top_prediction['disease_name']} in {top_prediction['location']}",
            },
            {
                'label': 'Total Cases',
                'value': f"{total_cases:,}",
                'detail': f"{len(case_records)} active records",
            },
            {
                'label': 'Top Disease',
                'value': top_disease['name'],
                'detail': f"{top_disease['cases']:,} cases logged",
            },
            {
                'label': 'Watchlist',
                'value': str(high_priority_count),
                'detail': 'High or critical records',
            },
        ],
        'report_lines': report_lines,
        'risk_predictions': risk_predictions,
        'trends': trends,
        'initial_note': generate_case_note(top_prediction),
        'top_case_id': top_prediction['id'],
    }


@app.route('/', methods=['GET'])
def index():
    total_cases = sum(item['case_count'] for item in CASE_RECORDS)
    disease_types = len({item['disease_name'] for item in CASE_RECORDS})
    locations_affected = len({item['location'] for item in CASE_RECORDS})
    critical_outbreaks = sum(
        1 for item in CASE_RECORDS
        if item['severity'] == 'Critical'
    )

    return render_template(
        'index.html',
        total_cases=f'{total_cases:,}',
        disease_types=disease_types,
        locations_affected=locations_affected,
        critical_outbreaks=critical_outbreaks,
        recent_cases=CASE_RECORDS,
        case_records=CASE_RECORDS,
    )

@app.route('/map', methods=['GET'])
def map_view():
    """ 
    Map view of disease cases using calling map_view.html
    map_view.html will use JavaScript to fetch case data and display it on a map
    """
    return render_template('map_view.html')


@app.route('/api/get_cases_data/', methods=['GET'])
def get_cases_data():
    """Return disease case data for the map markers."""
    return jsonify(CASE_DATA)


@app.route('/export', methods=['GET'])
def export_csv():
    output = StringIO()
    fieldnames = [
        'id',
        'disease_name',
        'severity',
        'location',
        'case_count',
        'date_reported',
        'notes',
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()

    for case_record in CASE_RECORDS:
        writer.writerow({
            'id': case_record['id'],
            'disease_name': case_record['disease_name'],
            'severity': case_record['severity'],
            'location': case_record['location'],
            'case_count': case_record['case_count'],
            'date_reported': case_record['date_reported'].isoformat(),
            'notes': case_record['notes'],
        })

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={
            'Content-Disposition': 'attachment; filename=disease_case_log.csv',
        },
    )

@app.route('/add', methods=['GET', 'POST'])
def add_case():
    if request.method == 'POST':
        form_data, errors = read_case_form()

        if not errors:
            form_data['id'] = get_next_case_id()
            CASE_RECORDS.insert(0, form_data)
            flash('Case record added successfully.', 'success')
            return redirect(url_for('index'))

        return render_template(
            'case_form.html',
            form_title='Add New Case',
            submit_label='Add Case',
            case_record=form_data,
            severity_levels=SEVERITY_LEVELS,
            errors=errors,
        )

    return render_template(
        'case_form.html',
        form_title='Add New Case',
        submit_label='Add Case',
        case_record={
            'disease_name': '',
            'severity': 'Moderate',
            'location': '',
            'case_count': 0,
            'date_reported': date.today(),
            'notes': '',
        },
        severity_levels=SEVERITY_LEVELS,
        errors={},
    )

@app.route('/edit/<int:case_id>', methods=['GET', 'POST'])
def edit_case(case_id):
    case_record = get_case_record(case_id)

    if case_record is None:
        abort(404)

    if request.method == 'POST':
        form_data, errors = read_case_form()

        if not errors:
            case_record.update(form_data)
            flash('Case record updated successfully.', 'success')
            return redirect(url_for('index'))

        form_data['id'] = case_id
        return render_template(
            'case_form.html',
            form_title='Edit Case',
            submit_label='Save Changes',
            case_record=form_data,
            severity_levels=SEVERITY_LEVELS,
            errors=errors,
        )

    return render_template(
        'case_form.html',
        form_title='Edit Case',
        submit_label='Save Changes',
        case_record=case_record,
        severity_levels=SEVERITY_LEVELS,
        errors={},
    )

@app.route('/delete/<int:case_id>', methods=['POST'])
def delete_case(case_id):
    case_record = get_case_record(case_id)

    if case_record is None:
        abort(404)

    CASE_RECORDS.remove(case_record)
    flash('Case record deleted successfully.', 'success')
    return redirect(url_for('index'))


@app.route('/ai_outbreak_analyst', methods=['GET'])
def ai_outbreak_analyst():
    analysis = build_outbreak_analysis(CASE_RECORDS)
    return render_template(
        'ai_outbreak_analyst.html',
        analysis=analysis,
        case_records=CASE_RECORDS,
    )


@app.route('/ai_analysis', methods=['POST'])
def ai_analysis():
    request_data = request.get_json(silent=True) or request.form

    try:
        case_id = int(request_data.get('case_id', 0))
    except (TypeError, ValueError):
        return jsonify({'error': 'Choose a valid case record.'}), 400

    case_record = get_case_record(case_id)
    if case_record is None:
        return jsonify({'error': 'Case record not found.'}), 404

    tone = request_data.get('tone', 'brief')
    if tone not in ('brief', 'operations', 'public'):
        tone = 'brief'

    return jsonify({
        'note': generate_case_note(case_record, tone),
        'case': {
            'id': case_record['id'],
            'disease_name': case_record['disease_name'],
            'location': case_record['location'],
        },
    })

if __name__ == '__main__':
    app.run(debug=True)
