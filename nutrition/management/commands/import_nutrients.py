#####################################################
# This script imports nutrients from a CSV file and creates Nutrient instances in the database.
# The CSV file must be located in the data folder.
# The CSV file must have the following columns:
# name, unit_abbreviation, isCategory, parentNutrient
#####################################################

import os
import csv
from django.core.management.base import BaseCommand
from nutrition.models import Nutrient, Unit

class Command(BaseCommand):
    help = 'Import nutrients from a CSV file'

    def handle(self, *args, **options):
        # Define the relative path to CSV file
        csv_file = os.path.normpath(os.path.join("data", "nutrients.csv"))

        try:
            # Open the CSV file and read its contents
            with open(csv_file, mode='r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)

                # Iterate through each row in the CSV
                for row in reader:
                    name = row['name']
                    unit_abbreviation = row['unit_abbreviation']
                    is_category = row['isCategory']
                    parent_nutrient = row['parentNutrient']

                    # Get or create the Unit object
                    unit, created = Unit.objects.get_or_create(abbreviation=unit_abbreviation)
                    
                    # Get or create the Nutrient object
                    nutrient, created = Nutrient.objects.get_or_create(name=name, unit=unit)
                    nutrient.isCategory = is_category.lower() == 'true'

                    # If a parent nutrient is specified, link it
                    if parent_nutrient:
                        try:
                            parent_nutrient = Nutrient.objects.get(name=parent_nutrient)
                            nutrient.parentNutrient = parent_nutrient
                        except Nutrient.DoesNotExist:
                            self.stdout.write(self.style.ERROR(f'Parent nutrient with name "{parent_nutrient}" does not exist.'))

                    nutrient.save()

                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Created nutrient: {name}'))
                    else:
                        self.stdout.write(self.style.SUCCESS(f'Updated nutrient: {name}'))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR('CSV file not found. Please check the file path.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred: {e}'))
