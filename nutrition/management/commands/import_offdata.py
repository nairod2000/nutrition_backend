import os
import json
import csv
from django.core.management.base import BaseCommand
from django.db import transaction
from nutrition.models import Item, ServingSize, Nutrient, Unit, ItemNutrient
import re
from tqdm import tqdm
from langdetect import detect



def getNutrientsAndUnits():
    nutriunits = {}
    nutrientCSV = os.path.normpath(os.path.join("data", "nutrients.csv"))
    with open(nutrientCSV, mode='r',encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        for row in reader:
            name = row['name'].lower()
            unit_abbreviation = row['unit_abbreviation']
            nutriunits[name] = unit_abbreviation
    return nutriunits

def parseServingSize(servingSize):
    numPart = ''
    unitPart = ''
    for i in range (len(servingSize)):
        if servingSize[i].isalpha():
            unitPart += servingSize[i]
        else:
            numPart += servingSize[i]

def parseNutrientsDict(nutrientsDict):
    for key,value in nutrientsDict.items():
        

class Command(BaseCommand):
    help = 'Import item data from a JSONL file'

    def handle(self, *args, **options):
        # Define the relative path to CSV file
        jsonl_file = os.path.normpath(os.path.join("data", "massagedData.jsonl"))
        nutrients = []
        serving_sizes = []
        items = []
        item_nutrients = []
        unit_gram, created = Unit.objects.get_or_create(name='gram', abbreviation='g')
        nutriunits = getNutrientsAndUnits()
        try:
            # Open the CSV file and read its contents
            with open(jsonl_file,'r',encoding='utf-8') as file:
                for food_item in tqdm(file,total=246385):
                    data = json.loads(food_item)
                    if data.get('serving_size') >= 10**5:
                        continue
                    serving_size = ServingSize(amount=round(float(data.get('serving_size')),2), unit=unit_gram)
                    serving_sizes.append(serving_size)
                    item = Item(
                        barcode=data.get('code'),
                        name=data.get('product_name'),
                        servingSize=serving_size,
                        calories=data.get('calories')
                    )
                    items.append(item)
                    for nutrient_name, nutrient_value in data.get('nutrients').items():
                        nutrient, created = Nutrient.objects.get_or_create(
                            name=nutrient_name,
                            defaults={'unit': unit_gram}
                        )
                        nutrient_value = round(float(nutrient_value),2)
                        if(nutrient_value >= 10**5):
                            continue
                        item_nutrient = ItemNutrient(
                            item=item,  # This will be set after saving items
                            nutrient=nutrient,
                            amount=nutrient_value
                        )
                        item_nutrients.append(item_nutrient)
            with transaction.atomic():
                print('Writing serving sizes to database...')
                # Bulk create all the serving sizes
                ServingSize.objects.bulk_create(serving_sizes, batch_size=1000)
                print('Done.')
                print('Writing items to database...')
                # Bulk create all the items and save the returned objects
                print('Creating items...')
                created_items = Item.objects.bulk_create(items, batch_size=1000)
                print('Done.')
                # Create a mapping from the old items to the new items
                print('Creating item mapping...')
                item_mapping = {item: created_item for item, created_item in zip(items, created_items)}
                print('Done.')
                # Update the item field of each ItemNutrient object
                print('Updating item nutrient foreign keys...')
                for item_nutrient in item_nutrients:
                    item_nutrient.item = item_mapping[item_nutrient.item]
                print('Done.')
                # Bulk create all the item nutrients
                print('Creating item nutrients...')
                ItemNutrient.objects.bulk_create(item_nutrients, batch_size=1000)
                print('Done.')

            self.stdout.write(self.style.SUCCESS('Successfully imported data.'))



        except FileNotFoundError:
            self.stdout.write(self.style.ERROR('JSONL file not found. Please check the file path.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred: {e}'))
