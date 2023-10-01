import os
import csv
from django.core.management.base import BaseCommand
from nutrition.models import GoalTemplate, Nutrient

class Command(BaseCommand):
    help = 'Import goal templates from a CSV file'

    def handle(self, *args, **options):
        # Define the relative path to CSV file
        csv_file = os.path.join("data", "goal_templates.csv")

        try:
            # Open the CSV file and read its contents
            with open(csv_file, 'r') as file:
                reader = csv.DictReader(file)
                
                # Iterate through each row in the CSV
                for row in reader:
                    # Extract attributes for UserGoal from the CSV row
                    name = row['name']
                    sex = row['sex']
                    is_pregnant = row['isPregnant']
                    is_lactating = row['isLactating']
                    age_min = row['ageMin']
                    age_max = row['ageMax']

                    # Create a UserGoal instance
                    goal_template = GoalTemplate.objects.create(
                        name=name,
                        sex=sex,
                        is_pregnant=is_pregnant,
                        is_lactating=is_lactating,
                        age_min=age_min,
                        age_max=age_max,
                    )

                    # Iterate through nutrient names in the CSV row and create UserGoalNutrient instances
                    for nutrient_name, recommended_value in row.items():
                        # Check if the column is a nutrient (skip non-nutrient columns)
                        if nutrient_name not in ('name', 'sex', 'isPregnant', 'isLactating', 'ageMin', 'ageMax'):
                            nutrient, created = Nutrient.objects.get_or_create(name=nutrient_name)
                            goal_template.nutrients.create(
                                nutrient=nutrient,
                                recommended_value=recommended_value,
                            )

                    self.stdout.write(self.style.SUCCESS(f'Created goal template: {goal_template}'))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR('CSV file not found. Please check the file path.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred: {e}'))
