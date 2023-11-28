import os
import json
import csv
from django.core.management.base import BaseCommand
from django.db import transaction
from nutrition.models import Item, ServingSize, Nutrient, Unit, ItemNutrient
import re
from tqdm import tqdm
from langdetect import detect





def getUnits():
    units = Unit.objects.all()
    unitList = []
    for unit in units:
        unitList.append(unit)
    return unitList

def getNutrients():
    nutrients = Nutrient.objects.all()
    nutrientList = []
    for nutrient in nutrients:
        nutrientList.append(nutrient)
    return nutrientList

def parseServings(servingSize):
    numPart = ""
    unitPart = ""
    for i in range(len(servingSize)):
        if servingSize[i].isalpha():
            unitPart += servingSize[i]
        else:
            numPart += servingSize[i]
    return numPart, unitPart

def checkUnitsForMatch(unit, unitList):
    unit_lower = unit.lower()
    for unitObj in unitList:
        if unitObj.name.lower()  == unit_lower or unitObj.abbreviation.lower() == unit_lower:
            return unitObj
    return None

def checkNutrientsForMatch(nutrient, nutrientList):
    nutrient_lower = nutrient.lower()
    for nutrientObj in nutrientList:
        if nutrientObj.name.lower() == nutrient_lower:
            return nutrientObj
    return None


def read_items(jsonl_file,batch_size=1000):
    items = []
    item_nutrients = []
    serving_sizes = []
    nutrients = getNutrients()
    units = getUnits()
    with open(jsonl_file,'r',encoding='utf-8') as file:
        for food_item in file:
            #load item into dictionary
            data = json.loads(food_item)
            #get the two options for serving size
            serving_size,unit = "",""
            serving_size_grams = data.get('serving_size_grams')
            serving_size_other = data.get('serving_size_other')
            #determine if the alternate serving size exists and if it does use that one otherwise use grams
            if serving_size_other == None:
                serving_size = serving_size_grams
                serving_size,unit = parseServings(serving_size)
            else:
                serving_size = serving_size_other
                if "kcal" in serving_size:
                    serving_size = serving_size_grams
                serving_size,unit = parseServings(serving_size)
            #if the unit is not in the unit table already we will need to create a new entry for that unit otherwise we will just use the existing one
            unitAbbreviation = ""
            # if unit in units:
            #     unitAbbreviation = units.get(unit)
            # else:
            #     unitAbbreviation = unit
            unitObj = checkUnitsForMatch(unit, units)
            if unitObj is None:
                unitObj, created = Unit.objects.get_or_create(
                    name=unit,
                    abbreviation=unit
                )
                units.append(unitObj)
            #if unit is already in the table we will just use that one otherwise we will create a new entry for that unit
            #create the serving size and add it to the list of serving sizes
            if serving_size == "" or serving_size == None:
                continue
            try:
                serving_size = round(float(serving_size),2)
                if serving_size >= 10**5:
                    continue
            except:
                continue
            servingSize = ServingSize(
                amount=serving_size,
                unit=unitObj
            )
            serving_sizes.append(servingSize)
            #create the item and add it to the list of items
            calories=data.get('calories')
            if calories is None:
                continue
            item = Item(
                barcode=data.get('barcode'),
                name=data.get('name'),
                servingSize=servingSize,
                calories=data.get('calories')
            )
            items.append(item)
            #parse the nutrients and add them to the list of item nutrients (units should already be in the unit table)
            #nutrients is a dictionary whose key is a nutrient name and value is another dictionary containing the amount per serving and the unit
            nutrientsDic = data.get('nutrients')
            for nutrient_name in nutrientsDic.keys():
                #forgot to remove these two from the data cleaning script
                if nutrient_name == "fruits-vegetables-nuts-estimate-from-ingredients" or nutrient_name == "energy-kcal_serving":
                    continue
                values = nutrientsDic.get(nutrient_name)
                amountPerServing = values.get('amount_per_serving')
                unit = values.get('unit')
                if amountPerServing > 10**5:
                    continue
                #same as the last creation of unit objects, if its in there well use it otherwise we will create a new one
                unitObj = checkUnitsForMatch(unit, units)
                if unitObj is None:
                    unitObj, created = Unit.objects.get_or_create(
                        name=unit,
                        abbreviation=unit
                    )
                    units.append(unitObj)
                #another example of checking for an object and creating it otherwise (sort of defeats the purpose of the generator but oh well)
                nutrient = checkNutrientsForMatch(nutrient_name, nutrients)
                if nutrient is None:
                    nutrient, created = Nutrient.objects.get_or_create(
                        name=nutrient_name,
                        unit = unitObj
                    )
                    nutrients.append(nutrient)
                item_nutrient = ItemNutrient(
                    item=item,  # This will be set after saving items
                    nutrient=nutrient,
                    amount=amountPerServing
                )
                item_nutrients.append(item_nutrient)
            #yielding items will significantly reduce the memory usage (generator)
            if(len(items) >= batch_size):
                yield items, item_nutrients, serving_sizes
                items = []
                item_nutrients = []
                serving_sizes = []
        if items:
            yield items, item_nutrients, serving_sizes


class Command(BaseCommand):
    help = 'Import item data from a JSONL file'

    def handle(self, *args, **options):
        # Define the relative path to JSONL file
        self.stdout.write(self.style.NOTICE('Starting import...'))
        jsonl_file = os.path.normpath(os.path.join("data", "newData2.jsonl"))
        try:
            counter = 1
            for items, item_nutrients, serving_sizes in read_items(jsonl_file):
                ServingSize.objects.bulk_create(serving_sizes)
                Item.objects.bulk_create(items)
                ItemNutrient.objects.bulk_create(item_nutrients)
                self.stdout.write(self.style.NOTICE("Batch " + str(counter) + " of 206 imported."))
                counter += 1


            self.stdout.write(self.style.SUCCESS('Successfully imported data.'))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR('JSONL file not found. Please check the file path.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred: {e}'))
