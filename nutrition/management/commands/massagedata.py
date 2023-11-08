import os
import json
from django.core.management.base import BaseCommand
from django.db import transaction
from nutrition.models import Item, ServingSize, Nutrient, Unit, ItemNutrient
import re
from tqdm import tqdm
from langdetect import detect


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
    help = 'Import item data from a JSONL file'

    def handle(self, *args, **options):
        # Define the relative path to CSV file
        jsonl_file = os.path.normpath(os.path.join("data", "openfoodfacts-products.jsonl"))
        dataFile = open("massagedData.jsonl", "w")

        try:
            # Open the CSV file and read its contents
            with open(jsonl_file,'r',encoding='utf-8') as file:
                for food_item in tqdm(file,total=2980745):
                    # Load the JSON data from each line
                    data = json.loads(food_item)
                    product_name = data.get('product_name')
                    if product_name:
                        try:
                            language = detect(product_name)
                        except:
                            continue
                        if language != 'en':
                            continue
                    # Skip items with missing data
                    if isAllZero(data.get('code')) or data.get('product_name') is None or data.get('product_name') == '' or data.get('nutriments') is None or data.get('serving_size') is None or data.get('nutriments').get('energy-kcal_100g') is None:
                        continue
                    serving_size_amount = data.get('serving_size')
                    massaged_data = {}
                    massaged_data['code'] = data.get('code')
                    massaged_data['product_name'] = data.get('product_name')
                    nutrients = data.get('nutriments')
                    nutrientsDict = {}
                    for key,value in nutrients.items():
                        nutrient_name = key  # e.g., 'sugar'
                        v = value
                        nutrientsDict[nutrient_name] = v
                    massaged_data['nutrients'] = nutrientsDict
                    massaged_data['calories'] = data.get('nutriments').get('energy-kcal_100g')
                    massaged_data['serving_size'] = serving_size_amount
                    dataFile.write(json.dumps(massaged_data))
                    dataFile.write("\n")

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR('JSONL file not found. Please check the file path.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred: {e}'))
        finally:
            dataFile.close()

    print("Done")
