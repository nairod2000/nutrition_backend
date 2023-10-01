import os
import csv
from django.core.management.base import BaseCommand
from nutrition.models import Nutrient, Unit

class Command(BaseCommand):
    help = 'Import nutrients from a CSV file'

    def handle(self, *args, **options):
        # Define the relative path to CSV file
        csv_file = os.path.join("data", "nutrients.csv")

        try:
            # Open the CSV file and read its contents
            with open(csv_file, mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    name = row['name']
                    unit_name = row['unit']
                    is_category = row['isCategory']
                    parent_name = row['parentNutrient']

                    # Get or create the Unit object
                    unit, created = Unit.objects.get_or_create(name=unit_name)

                    # Get or create the Nutrient object
                    nutrient, created = Nutrient.objects.get_or_create(name=name)
                    nutrient.unit = unit
                    nutrient.isCategory = is_category.lower() == 'true'

                    # If a parent nutrient is specified, link it
                    if parent_name:
                        parent_nutrient, created = Nutrient.objects.get_or_create(name=parent_name)
                        nutrient.parentNutrient = parent_nutrient

                    nutrient.save()

                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Created nutrient: {name}'))
                    else:
                        self.stdout.write(self.style.SUCCESS(f'Updated nutrient: {name}'))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR('CSV file not found. Please check the file path.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred: {e}'))
