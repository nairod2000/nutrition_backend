# Data Importers

The data importers are used to import data from CSV files into the database. The importers are located in the `nutrition/management/commands/` directory. The csv data files are located in the `data/` directory.

## Importing Data

To import data, run the following commands:

## A word about openfoodfacts data

Here is a link to the data dump in JSONL format: https://static.openfoodfacts.org/data/openfoodfacts-products.jsonl.gz
Compressed it is about 6.5 gigs, uncompressed, it is about 40 gigs...
This importer aims to skip "bad" data e.g. no barcode, weird serving size, other oddities
As i am writing this documentation it has been running for about 15 minutes and i have no idea when it plans on stopping.


```bash
python manage.py import_units
```
```bash
python manage.py import_nutrients
```
```bash
python manage.py import_goal_template
```
```bash
python manage.py import_openfoodfacts_data
```

on a side note if you wish to clean the db (wipe out all the existing data) you can run

```bash
python manage.py flush
```
you will then be asked to confirm your decision by typing yes in the console and furthermore this will delete your superuser account so you will need to create it again
refer to README.md for instructions on how to do that
