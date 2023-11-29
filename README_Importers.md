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
python manage.py import_goal_templates
```
```bash
python manage.py finalimporter3
```

## A Word About OpenFoodFacts Data (finalimporter)

I wrote a script (massagedata.py) that went through the entire jsonl file and wrote the pertinent data for each entry to a new jsonl file that conatins only data in English and that also has the data we care about (name, barcodes, serving sizes, nutrients). That file is about 100+ mb rather than the 40 gb of the initial file (most of that file size came from all the additional data that was in each entry, e.g., the tags and such they use for their search algorithm). This massaged data can be downloaded from https://drive.google.com/file/d/1rn6_LdD2xLvHrBkxQhHA4pogoWhCMSR_/view?usp=sharing On the other hand, if you would rather go through the process of massaging the data yourself, do be warned; it takes about 6 hours. Using the massaged data, the new importer takes about 30 minutes.

On a side note, if you wish to clean the database (wipe out all the existing data), you can run the following:

```bash
python manage.py flush
```

You will then be asked to confirm your decision by typing yes. This will delete your superuser account so you will need to create it again. Refer to README.md for instructions on how to do that.
