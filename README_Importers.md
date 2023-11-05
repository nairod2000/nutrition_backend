# Data Importers

The data importers are used to import data from CSV files into the database. The importers are located in the `nutrition/management/commands/` directory. The csv data files are located in the `data/` directory.

## Importing Data

To import data, run the following commands:

## A word about openfoodfacts data

I wrote a script (massagedata.py) that went through the entire jsonl file and wrote the pertinent data for each entry to a new jsonl file
that conatins only data in english and that also has the data we care about (name,barcodes,serving sizes, nutrients) that file sits at just about
100+ mb rather than the 40 of the initial file (most of that file size came from all the additional data that was in each entry e.g. the tags and such they use for their search
algorithm) anyway the massaged data can be downloaded from https://gofile.io/d/zXEVLX if you want to go through the process of massaging the data yourself do be warned it takes
about 6 hours. the new importer takes about 30 minutes


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
python manage.py import_offdata.py
```

on a side note if you wish to clean the db (wipe out all the existing data) you can run

```bash
python manage.py flush
```
you will then be asked to confirm your decision by typing yes in the console and furthermore this will delete your superuser account so you will need to create it again
refer to README.md for instructions on how to do that
