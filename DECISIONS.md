# Engineering Decisions

## 1. Use Django + SQLite

**Decision:** Use Django with SQLite for the backend and database.

**Alternative:** PostgreSQL or another relational database.

**Reason:** Django provides the ORM, management commands, REST API support, and testing framework needed for the assignment. SQLite keeps the setup simple and portable for a take-home project.

---

## 2. Store source records before reconciliation

**Decision:** Import System A and System B into separate database models before running reconciliation.

**Alternative:** Compare the CSV files directly in memory.

**Reason:** Persisting the imported records makes the reconciliation process repeatable, inspectable, and easier to test.

---

## 3. Normalize record references before comparison

**Decision:** Normalize record references from both systems before matching them.

**Alternative:** Require the source systems to use exactly the same reference format.

**Reason:** The supplied data contains inconsistent reference formats such as `REC-1001` and `REC1001`. Normalization allows both values to represent the same logical record.

---

## 4. Preserve invalid numeric data as NULL

**Decision:** Convert non-parseable numeric values to `NULL` instead of silently dropping the row.

**Alternative:** Skip invalid rows or fail the entire import.

**Reason:** The assignment explicitly requires the importer to survive dirty data without silently dropping rows. Keeping the row allows the issue to remain visible for later investigation.

---

## 5. Store disagreements as database records

**Decision:** Persist reconciliation disagreements in a dedicated `Disagreement` model.

**Alternative:** Generate disagreement results only when the dashboard is requested.

**Reason:** Storing the results makes reconciliation output easy to inspect, expose through an API, and test independently from the UI.

---

## 6. Use a Django management command for reconciliation

**Decision:** Implement reconciliation as the `reconcile` management command.

**Alternative:** Run reconciliation automatically during every API request.

**Reason:** Reconciliation is a data-processing operation rather than a page-rendering operation. A management command makes it explicit, repeatable, and easy to run after importing new data.

---

## 7. Keep the dashboard simple

**Decision:** Use a server-rendered Django template with HTML, CSS, and JavaScript.

**Alternative:** Build a separate React frontend.

**Reason:** The assignment prioritizes correctness and working reconciliation behavior over visual design. A lightweight frontend reduced setup overhead while still providing the required filtering, sorting, and disagreement display.