# Brooks

Brooks is a Django REST Framework backend for tracking expenses. The first
implemented domain is vehicle refueling, but the project now has a separate
universal expense layer that can aggregate spending from any current or future
category.

## What the project does

The application currently supports:

- user registration and token login;
- vehicles owned by a user;
- gas stations;
- refueling records with mileage, fuel quantity, price, discount, and total cost;
- a universal expense table for all spending categories;
- editable expense categories;
- Swagger/OpenAPI documentation;
- Django admin.

The important design point is that refueling is not the main finance table.
Refueling is only the first detailed source of spending data. The finance layer
lives in the `expenses` app.

## Applications

### `forge`

`forge` contains vehicle and fuel-specific entities:

- `Vehicle` - a user's vehicle.
- `GasStation` - gas station directory.
- `Refueling` - a detailed fuel purchase/refueling record.
- `FuelPrice` - fuel price by date/type/station.
- `FuelStatistics` - fuel-specific aggregated statistics.

This app is responsible for domain details that only make sense for fuel:
mileage, odometer calculation, liters, fuel type, price per liter, full tank,
gas station, and fuel consumption.

### `expenses`

`expenses` is the universal spending layer.

It is intentionally separate from `forge`, because not every expense is related
to a car. Future categories can include food, rent, subscriptions, repairs,
insurance, parking, service, taxes, or any other spending type.

The app contains:

- `ExpenseCategory` - editable category dictionary.
- `Expense` - universal expense row.

## Universal Expense Table

The main aggregate table is:

```text
expenses_expense
```

It stores one normalized expense row regardless of where the expense came from.

Main fields:

```text
date          expense date
category_id   link to expenses_expensecategory
amount        final money amount
description   short human-readable text
user_id       owner of the expense
source_app    optional source application name
source_model  optional source model name
source_id     optional source object id
metadata      optional JSON payload for source-specific extra data
created_at
updated_at
```

There is no `vehicle_id` in this table. This is deliberate. The table must stay
universal and usable for expenses that have nothing to do with vehicles.

If an expense comes from a vehicle-related source, that relationship remains in
the source table. For example, `forge_refueling` has `vehicle_id`; the aggregate
expense row only points back to that source record.

## How Refueling Becomes an Expense

When a `Refueling` record is created or updated, Django signals in
`forge.models` automatically synchronize a row in `expenses_expense`.

Example:

```text
forge_refueling.id = 1
date = 2026-05-29
total_cost = 20000.00
discount = 0.00
vehicle = "ниссан"
```

The system creates:

```text
expenses_expense
date = 2026-05-29
category = fuel
amount = 20000.00
description = "Заправка ниссан"
source_app = "forge"
source_model = "refueling"
source_id = 1
```

The source fields mean:

```text
source_app    which app produced the expense
source_model  which source model produced it
source_id     source row id
```

For refueling:

```text
source_app = forge
source_model = refueling
source_id = forge_refueling.id
```

This gives the project both views:

- detailed fuel data remains in `forge_refueling`;
- common financial reporting uses `expenses_expense`.

If the refueling is edited, the related expense row is updated. If the refueling
is deleted, the related expense row is deleted.

## Expense Categories

Categories are stored in:

```text
expenses_expensecategory
```

Seeded categories:

```text
fuel
service
repair
insurance
parking
wash
toll
tax
other
```

Categories are database records, not hardcoded enum values. New categories can
be added through Django admin or the API without changing the `Expense` table
structure.

## API Endpoints

Swagger UI:

```text
GET /api/
```

OpenAPI schema:

```text
GET /api/schema/
```

Auth:

```text
POST /user/register/
POST /user/login/
```

Fuel and vehicle domain:

```text
/vehicle/
/refuelings/
/gasStation/
/fuel-statistics/
```

Universal expenses:

```text
/expense-categories/
/expenses/
/expenses/summary/
```

Useful filters:

```text
GET /expenses/?category=fuel
GET /expenses/?date_from=2026-05-01&date_to=2026-05-31
```

`/expenses/summary/` groups expenses by date and category and returns summed
amounts.

## Local Setup

Create a virtual environment and install dependencies:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Apply migrations:

```bash
.venv/bin/python manage.py migrate
```

Run tests:

```bash
.venv/bin/python -m pytest
```

Start the development server:

```bash
.venv/bin/python manage.py runserver 127.0.0.1:8000
```

Open:

```text
http://127.0.0.1:8000/api/
http://127.0.0.1:8000/admin/
```

## Admin

Create an admin user:

```bash
.venv/bin/python manage.py createsuperuser
```

For the current local development database, an admin user was created manually:

```text
username: admin
password: admin123456
```

Do not use this password outside local development.

## Current Database Shape

Main project tables:

```text
auth_user
users_users
forge_vehicle
forge_gasstation
forge_refueling
forge_fuelprice
forge_fuelstatistics
expenses_expensecategory
expenses_expense
```

Important relationships:

```text
auth_user 1 -> many forge_vehicle
auth_user 1 -> many forge_refueling
auth_user 1 -> many expenses_expense

expenses_expensecategory 1 -> many expenses_expense

forge_vehicle 1 -> many forge_refueling
forge_gasstation 1 -> many forge_refueling
forge_refueling 1 -> 1 expenses_expense
```

The last relation is represented by source fields, not by a direct foreign key:

```text
expenses_expense.source_app = "forge"
expenses_expense.source_model = "refueling"
expenses_expense.source_id = forge_refueling.id
```

This keeps the aggregate expense layer independent from any one domain.
