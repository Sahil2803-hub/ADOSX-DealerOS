# DealerOS Reconciliation System

A full-stack reconciliation application built for the ADOSX / DealerOS take-home assignment.

The application imports records from System A and System B, normalizes inconsistent references, detects reconciliation disagreements, stores the results, and presents them through a web dashboard.

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