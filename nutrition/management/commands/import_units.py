#####################################################
# This script imports units from a CSV file and creates Unit instances in the database.
# The CSV file must be located in the data folder.
# The CSV file must have the following columns:
# name, abbreviation
#####################################################

import os
import csv
from django.core.management.base import BaseCommand
from nutrition.models import Unit

class Command(BaseCommand):
    help = 'Import units from a CSV file'

    def handle(self, *args, **options):
        # Define the relative path to CSV file with double backslashes
        csv_file = os.path.normpath(os.path.join("data", "units.csv"))

        try:
            # Open the CSV file and read its contents
            with open(csv_file, mode='r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)

                # Iterate through each row in the CSV
                for row in reader:
                    name = row['name']
                    abbreviation = row['abbreviation']

                    # Create or update the Unit object
                    unit, created = Unit.objects.get_or_create(name=name, abbreviation=abbreviation)
                    unit.save()

                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Created unit: {name}'))
                    else:
                        self.stdout.write(self.style.SUCCESS(f'Updated unit: {name}'))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR('CSV file not found. Please check the file path.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred: {e}'))
