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

def isAllAscii(s):
    return all(ord(c) < 128 for c in s)

def parse_float_from_string(input_string):
    match = re.match(r'^\d*\.?\d+', input_string)
    if match:
        return float(match.group())
    else:
        raise ValueError("No leading number found in string")
    
def parse_serving_size(serving_size_str):
    # Regex pattern to match serving size in grams and in parentheses
    pattern = r'(\d+g) \(([^)]+)\)'
    match = re.search(pattern, serving_size_str)
    print(match)
    if match:
        serving_size_grams = match.group(1)
        serving_size_parentheses = match.group(2)
        return serving_size_grams, serving_size_parentheses
    else:
        return None, None
    

class Command(BaseCommand):
    help = 'Import item data from a JSONL file'

    def handle(self, *args, **options):
        # Define the relative path to CSV file
        jsonl_file = os.path.normpath(os.path.join("data", "massagedData.jsonl"))
        dataFile = open("fixedData2.jsonl", "w")

        try:
            # Open the CSV file and read its contents
            with open(jsonl_file,'r',encoding='utf-8') as file:
                for food_item in tqdm(file,total=248013):
                    # Load the JSON data from each line
                    data = json.loads(food_item)
                    product_name = data.get('product_name')
                    serving_size_grams, serving_size_other = parse_serving_size(data.get('serving_size'))
                    massaged_data = {}
                    massaged_data['code'] = data.get('code')
                    massaged_data['product_name'] = product_name
                    nutrients = data.get('nutrients')
                    massaged_data['nutrients'] = nutrients
                    massaged_data['calories'] = data.get('calories')
                    massaged_data['serving_size_grams'] = serving_size_grams
                    massaged_data['serving_size_other'] = serving_size_other
                    dataFile.write(json.dumps(massaged_data))
                    dataFile.write("\n")

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR('JSONL file not found. Please check the file path.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred: {e}'))
        finally:
            dataFile.close()

    print("Done")
