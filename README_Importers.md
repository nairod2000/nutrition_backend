# Data Importers

The data importers are used to import data from CSV files into the database. The importers are located in the `nutrition/management/commands/` directory. The csv data files are located in the `data/` directory.

## Importing Data

To import data, run the following commands:

```bash
python manage.py import_units
```
```bash
python manage.py import_nutrients
```
```bash
python manage.py import_goal_template
```
