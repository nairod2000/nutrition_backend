import os
import csv
from django.core.management.base import BaseCommand
from nutrition.models import Unit

class Command(BaseCommand):
    help = 'Import units from a CSV file'

    def handle(self, *args, **options):
        # Define the relative path to CSV file (this formats it correctly with double backslashes)
        csvFile = os.path.join("data", "units.csv")

        try:
            # Open file
            with open(csvFile, mode='r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)

                # Iterate through each row in the CSV
                for row in reader:
                    name = row['name']
                    abbreviation = row['abbreviation']

                    # Get or create the Unit
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
