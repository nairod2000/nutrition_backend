import os
import csv
from django.core.management.base import BaseCommand
from nutrition.models import GoalTemplate, GoalTemplateNutrient, Nutrient

class Command(BaseCommand):
    help = 'Import goal templates from a CSV file'

    def handle(self, *args, **options):
        # Define the relative path to CSV file (this formats it correctly with double backslashes)
        csvFile = os.path.join("data", "goal_templates.csv")

        try:
            # Open file
            with open(csvFile, mode='r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                
                # Iterate through each row in the CSV
                for row in reader:
                    name = row['name']
                    sex = row['sex']
                    isPregnant = row['isPregnant']
                    isLactating = row['isLactating']
                    age_min = row['ageMin']
                    age_max = row['ageMax']

                    # Create a GoalTemplate
                    goal_template, created = GoalTemplate.objects.get_or_create(
                        name=name,
                        sex=sex,
                        isPregnant=isPregnant,
                        isLactating=isLactating,
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

                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Created goal template: {goal_template}'))
                    else:
                        self.stdout.write(self.style.SUCCESS(f'Updated goal template: {goal_template}'))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR('CSV file not found. Please check the file path.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred: {e}'))
