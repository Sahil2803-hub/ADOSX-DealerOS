# DealerOS Reconciliation System

A reconciliation application built for the ADOSX / DealerOS take-home assignment.

The application imports records from System A and System B, handles dirty data, normalizes inconsistent record references, detects reconciliation disagreements, stores the results, and presents them through a tenant-aware web dashboard.

## Tech Stack

- Python
- Django
- Django REST Framework
- SQLite
- HTML
- CSS
- JavaScript
- Git

## Features

### Data Import

The application imports:

- `locations.csv`
- `system_a.csv`
- `system_b.csv`

The importer is designed to handle dirty data without silently dropping rows.

It handles:

- Blank values
- Invalid numeric values
- Invalid dates
- Inconsistent record reference formats
- Orphan System B references

Invalid numeric values are stored as `NULL` where appropriate and reported by the importer.

### Record Normalization

System A and System B can use different reference formats.

For example:

```text
REC-1001
REC1001
```

These references are normalized before reconciliation so that formatting differences do not incorrectly create missing or orphan records.

### Reconciliation

The reconciliation process detects:

- Missing in System B
- Orphan System B records
- Duplicate System B records
- Value mismatches

The reconciliation results are stored in the `Disagreement` database table.

### Tenant Isolation

The dashboard and API support organization-level filtering.

Each location belongs to an organization through the `locations.csv` data.

The disagreement API requires an `org_id` parameter and filters results to locations belonging to that organization.

For example:

```text
/api/disagreements/?org_id=ORG-A
```

If no organization is supplied, the API returns a `400 Bad Request` instead of exposing disagreements across all organizations.

The tenant boundary was tested using both `ORG-A` and `ORG-B`.

In a production application with authentication, the organization would be derived from the authenticated user's identity rather than supplied directly by the client.

## Dashboard

The dashboard provides:

- Total disagreement count
- Missing in B count
- Orphan B count
- Duplicate B count
- Value mismatch count
- Organization selector
- Disagreement reason filter
- Value sorting
- Refresh functionality
- Detailed disagreement table

The dashboard is intentionally kept simple because the assignment prioritizes correctness and reconciliation behavior over visual design.

## API Endpoints

### Dashboard

```text
GET /api/
```

Opens the reconciliation dashboard.

### Disagreement List

```text
GET /api/disagreements/?org_id=ORG-A
```

Returns disagreements for a specific organization.

Example response:

```json
{
    "count": 1,
    "results": [
        {
            "id": 1,
            "record_ref": "REC-1003",
            "reason": "value_mismatch",
            "system_a_value": 121388.01,
            "system_b_value": 94834.38,
            "location_id": "LOC-202"
        }
    ]
}
```

Calling the endpoint without an organization:

```text
GET /api/disagreements/
```

returns:

```json
{
    "error": "org_id query parameter is required."
}
```

### Reconciliation Summary

```text
GET /api/summary/?org_id=ORG-A
```

Returns the disagreement counts for an organization.

## Project Structure

```text
ADOSX-DealerOS/
│
├── backend/
│   ├── config/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── ...
│   │
│   ├── reconciliation/
│   │   ├── management/
│   │   │   └── commands/
│   │   │       ├── import_data.py
│   │   │       └── reconcile.py
│   │   │
│   │   ├── migrations/
│   │   ├── templates/
│   │   │   └── dashboard.html
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   │
│   ├── db.sqlite3
│   ├── manage.py
│   └── requirements.txt
│
├── data/
│   ├── locations.csv
│   ├── system_a.csv
│   └── system_b.csv
│
├── DECISIONS.md
├── README.md
└── .gitignore
```

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/Sahil2803-hub/ADOSX-DealerOS.git
cd ADOSX-DealerOS
```

### 2. Create a virtual environment

Windows:

```powershell
python -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
cd backend
pip install -r requirements.txt
```

### 4. Run migrations

```powershell
python manage.py migrate
```

### 5. Import the supplied data

From the `backend` directory:

```powershell
python manage.py import_data
```

The importer reads the CSV files from the project's `data/` directory.

### 6. Run reconciliation

```powershell
python manage.py reconcile
```

The command clears previous reconciliation results and generates the current disagreement results.

### 7. Start the development server

```powershell
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/api/
```

## Testing

The project includes tests for each required disagreement type:

- Missing in B
- Orphan B
- Duplicate B
- Value mismatch

Run the tests with:

```powershell
python manage.py test reconciliation
```

The current test suite contains four reconciliation tests and all four pass.

## Reconciliation Result

When the supplied dataset is imported and reconciled, the application identifies disagreement records across the two systems.

The dashboard allows the results to be viewed by organization and filtered by disagreement reason.

The supplied dataset produces 13 disagreement records in total across the organizations.

## Data Handling Decisions

The importer uses defensive parsing for dates and numeric values.

Malformed values are not allowed to crash the entire import process. Instead, invalid values are represented as `NULL` where appropriate and reported by the importer.

Record references are normalized before comparison so that formatting differences such as hyphens, underscores, spaces, and case do not cause false reconciliation failures.

Further engineering decisions are documented in:

```text
DECISIONS.md
```

## What Was Built

- CSV data importer
- Dirty-data handling
- Record reference normalization
- System A / System B reconciliation
- Missing record detection
- Orphan record detection
- Duplicate record detection
- Value mismatch detection
- Tenant-aware API filtering
- REST API endpoints
- Reconciliation dashboard
- Reason filtering
- Value sorting
- Automated reconciliation tests
- Project documentation
- Git commit history

## What Was Not Built

The following production features were intentionally kept outside the scope of this assignment:

- User authentication
- Authorization based on real user accounts
- Production deployment
- Advanced UI design
- Performance optimization for very large datasets
- Full production audit logging
- Separate React frontend

The dashboard uses a lightweight Django template with HTML, CSS, and JavaScript to keep the implementation focused on the reconciliation requirements.

## How I Worked With the Agent

AI assistance was used during development for:

- Project scaffolding
- Django model design
- Importer implementation
- Reconciliation logic
- API implementation
- Dashboard implementation
- Debugging
- Test creation
- Documentation

The generated code was reviewed, tested, and corrected during development.

### 1. What is one thing the AI agent got wrong?

One issue was the initial reconciliation matching logic.

System A used references such as:

```text
REC-1001
```

while System B could contain the same reference in a different format:

```text
REC1001
```

The initial implementation did not normalize both sides consistently, which caused many valid records to be incorrectly classified as missing or orphaned.

I identified the problem by checking the reconciliation results and corrected the implementation so that both System A and System B references are normalized before comparison.

### 2. Which area are you least confident about?

The area I am least confident about is production-grade tenant isolation.

The current implementation requires an `org_id` parameter and filters disagreements through the location-to-organization relationship. The API was tested to ensure that organization-specific requests return only records belonging to that organization, while requests without an organization are rejected.

In a production system, I would derive the organization from the authenticated user's session or access token rather than trusting a query parameter supplied by the client.

### 3. If you had a second day, what would you improve?

With another day, I would improve the system in three main areas:

1. Add proper authentication and authorization so the organization is derived from the authenticated user.
2. Improve importer auditing with row-level error reporting and preservation of invalid source values where appropriate.
3. Expand automated tests around tenant isolation, malformed input, duplicate records, and edge cases in reference normalization.

## Verification

Before submission, the application was verified by:

- Running the Django development server
- Running the data importer
- Running the reconciliation command
- Running Django system checks
- Running the automated reconciliation tests
- Testing the dashboard
- Testing organization-specific API responses
- Testing that requests without `org_id` are rejected

The reconciliation tests pass for all four required disagreement types.

## Assignment Scope

Authentication and deployment were intentionally skipped because they were outside the required implementation scope.

The implementation focuses on the main evaluation areas:

- Correct reconciliation
- Handling messy input data
- Tenant boundaries
- Automated tests
- Clear documentation

## License

This project was created as a take-home assignment for ADOSX / DealerOS.
