import os
import json
from django.core.management.base import BaseCommand
from django.db import transaction
from nutrition.models import Item, ServingSize, Nutrient, Unit, ItemNutrient
import re
from tqdm import tqdm


def isAllZero(code):
    for i in code:
        if i != '0':
            return False
    return True

def isServing(size):
    return None

def parse_float_from_string(input_string):
    match = re.match(r'^\d*\.?\d+', input_string)
    if match:
        return float(match.group())
    else:
        raise ValueError("No leading number found in string")



class Command(BaseCommand):
    help = 'Import item data from a CSV file'

    def handle(self, *args, **options):
        # Define the relative path to CSV file
        jsonl_file = os.path.normpath(os.path.join("data", "openfoodfacts-products.jsonl"))

        try:
            # Open the CSV file and read its contents
            with open(jsonl_file,'r',encoding='utf-8') as file:
                for food_item in tqdm(file,total=2980745):
                    # Load the JSON data from each line
                    data = json.loads(food_item)
                    if isAllZero(data.get('code')) or data.get('product_name') is None or data.get('nutriments') is None or data.get('serving_size') is None or data.get('nutriments').get('energy-kcal_100g') is None or data.get('serving_size').isalpha():
                        continue

                    # Create a new unit object
                    try:
                        unit_gram, created = Unit.objects.get_or_create(name='gram', abbreviation='g')
                    except Unit.MultipleObjectsReturned:
                        unit_gram = Unit.objects.filter(name='gram').first()
                    #get nutrients
                    nutrients = data.get('nutriments')
                    for key,value in nutrients.items():
                        if key.endswith("_serving"):
                            nutrient_name = key.replace("_serving", "")  # e.g., 'sugar'
                            amount_per_100g = value
                            nutrient, created = Nutrient.objects.get_or_create(name=nutrient_name,
                                                            defaults={'unit': unit_gram})
                    #create a serving size
                    try:
                        serving_size_amount = parse_float_from_string(data.get('serving_size'))
                    except ValueError:
                        serving_size_amount = 1.0
                    try:
                        serving_size,created = ServingSize.objects.get_or_create(amount=serving_size_amount,unit=unit_gram)
                    except:
                        serving_size = ServingSize.objects.filter(amount=serving_size_amount,unit=unit_gram).first()
                    # Create a new item object
                    item, created = Item.objects.get_or_create(
                        barcode=data.get('code'),
                        defaults={
                            'name': data.get('product_name'),
                            'calories': data.get('nutriments').get('energy-kcal_100g'),
                            'servingSize': serving_size,
                        }
                    )
                    item.save()



            print("Imported {} items from {}".format(Item.objects.count(), jsonl_file))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR('JSONL file not found. Please check the file path.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred: {e}'))