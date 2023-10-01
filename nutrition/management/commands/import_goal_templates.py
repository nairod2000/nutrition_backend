#####################################################
# This script imports goal templates from a CSV file and creates GoalTemplate instances in the database.
# The CSV file must be located in the data folder.
# The CSV file must have the following columns:
# name, sex, isPregnant, isLactating, ageMin, ageMax, and additional column headers containing the names of each template nutrient.
# PRECONDITION: Nutrients must already exist in the database (in the Nutrients table).
#   If a nutrient does not exist, that nutrient will be skipped and won't be included with the goal template.
#####################################################

import os
import csv
from django.core.management.base import BaseCommand
from nutrition.models import GoalTemplate, GoalTemplateNutrient, Nutrient

class Command(BaseCommand):
    help = 'Import goal templates from a CSV file'

    def handle(self, *args, **options):
        # Define the relative path to CSV file
        csv_file = os.path.join("data", "goal_templates.csv")

        try:
            # Open the CSV file and read its contents
            with open(csv_file, mode='r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                
                # Iterate through each row in the CSV
                for row in reader:
                    name = row['name']
                    sex = row['sex']
                    is_pregnant = row['isPregnant']
                    is_lactating = row['isLactating']
                    age_min = row['ageMin']
                    age_max = row['ageMax']

                    # Create a UserGoal instance
                    goal_template, created = GoalTemplate.objects.get_or_create(
                        name=name,
                        sex=sex,
                        isPregnant=is_pregnant,
                        isLactating=is_lactating,
                        ageMin=age_min,
                        ageMax=age_max,
                    )

                    # Iterate through nutrient names in the CSV row and create or update GoalTemplateNutrient instances
                    for nutrient_name, recommended_value in row.items():
                        # Check if the column is a nutrient (skip non-nutrient columns)
                        if nutrient_name not in ('name', 'sex', 'isPregnant', 'isLactating', 'ageMin', 'ageMax'):
                            try:
                                nutrient = Nutrient.objects.get(name=nutrient_name)
                            except Nutrient.DoesNotExist:
                                self.stdout.write(self.style.ERROR(f'Nutrient with name "{nutrient_name}" does not exist in the database.'))

                            # Set recommended value to 0 if empty or null
                            if not recommended_value:
                                recommended_value = 0

                            # Create or update GoalTemplateNutrient
                            goal_template_nutrient, created = GoalTemplateNutrient.objects.get_or_create(
                                nutrient=nutrient,
                                template=goal_template,
                                defaults={'recommendedValue': recommended_value},
                            )

                            # If not created (i.e., already exists), update the recommended value
                            if not created:
                                goal_template_nutrient.recommendedValue = recommended_value
                                goal_template_nutrient.save()

                    self.stdout.write(self.style.SUCCESS(f'Created or updated goal template: {goal_template}'))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR('CSV file not found. Please check the file path.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred: {e}'))
