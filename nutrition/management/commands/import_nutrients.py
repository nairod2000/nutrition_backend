import os
import csv
from django.core.management.base import BaseCommand
from nutrition.models import Nutrient, Unit

class Command(BaseCommand):
    help = 'Import nutrients from a CSV file'

    def handle(self, *args, **options):
        # Define the relative path to CSV file (this formats it correctly with double backslashes)
        csvFile = os.path.join("data", "nutrients.csv")

        try:
            # Open file
            with open(csvFile, mode='r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)

                # Iterate through each row in the CSV
                for row in reader:
                    name = row['name']
                    unitAbbreviation = row['unit_abbreviation']
                    isCategory = row['isCategory']
                    parentNutrient = row['parentNutrient']

                    # Get or create the Unit
                    unit, created = Unit.objects.get_or_create(abbreviation=unitAbbreviation)
                    
                    # Get or create the Nutrient
                    nutrient, created = Nutrient.objects.get_or_create(name=name, unit=unit)
                    nutrient.isCategory = isCategory.lower() == 'true'

                    # If a parent nutrient is specified, link it
                    if parentNutrient:
                        try:
                            parentNutrient = Nutrient.objects.get(name=parentNutrient)
                            nutrient.parentNutrient = parentNutrient
                        except Nutrient.DoesNotExist:
                            self.stdout.write(self.style.ERROR(f'Parent nutrient with name "{parentNutrient}" does not exist.'))

                    nutrient.save()

                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Created nutrient: {name}'))
                    else:
                        self.stdout.write(self.style.SUCCESS(f'Updated nutrient: {name}'))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR('CSV file not found. Please check the file path.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred: {e}'))
