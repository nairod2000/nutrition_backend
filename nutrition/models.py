from django.db import models

# Create your models here.
class Users(models.Model):
    id = models.AutoField(primary_key=True)
    userName = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    joinedOn = models.DateTimeField(auto_now_add=True)

class FoodItem(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    barcode = models.CharField(max_length=50)
    calories = models.IntegerField()
    protein = models.IntegerField()
    carbs = models.IntegerField()
    fats = models.IntegerField()
    unit = models.CharField(max_length=50)
    servingSize = models.IntegerField()

class Supplement(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    barcode = models.CharField(max_length=50)

class Vitamin(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    unit = models.CharField(max_length=50)

class Mineral(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    unit = models.CharField(max_length=50)

class CombinedItem(models.Model):
    id = models.AutoField(primary_key=True)
    userId = models.ForeignKey(Users, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

class Consumed(models.Model):
    id = models.AutoField(primary_key=True)
    userId = models.ForeignKey(Users, on_delete=models.CASCADE)
    foodId = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    supplementId = models.ForeignKey(Supplement, on_delete=models.CASCADE)
    combinedItemId = models.ForeignKey(CombinedItem, on_delete=models.CASCADE)
    consumedAt = models.DateTimeField(auto_now_add=True)
    portion = models.IntegerField()

class CombinedFoodElement(models.Model):
    id = models.AutoField(primary_key=True)
    combinedFoodId = models.ForeignKey(CombinedItem, on_delete=models.CASCADE)
    foodId = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    servingSize = models.IntegerField()

class FoodVitamin(models.Model):
    id = models.AutoField(primary_key=True)
    foodId = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    vitaminId = models.ForeignKey(Vitamin, on_delete=models.CASCADE)
    amount = models.IntegerField()

class FoodMineral(models.Model):
    id = models.AutoField(primary_key=True)
    foodId = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    mineralId = models.ForeignKey(Mineral, on_delete=models.CASCADE)
    amount = models.IntegerField()

class SupplementVitamin(models.Model):
    id = models.AutoField(primary_key=True)
    supplementId = models.ForeignKey(Supplement, on_delete=models.CASCADE)
    vitaminId = models.ForeignKey(Vitamin, on_delete=models.CASCADE)
    amount = models.IntegerField()

class SupplementMineral(models.Model):
    id = models.AutoField(primary_key=True)
    supplementId = models.ForeignKey(Supplement, on_delete=models.CASCADE)
    mineralId = models.ForeignKey(Mineral, on_delete=models.CASCADE)
    amount = models.IntegerField()

class SupplementIngredient(models.Model):
    id = models.AutoField(primary_key=True)
    supplementId = models.ForeignKey(Supplement, on_delete=models.CASCADE)
    foodId = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    amount = models.IntegerField()
    unit = models.CharField(max_length=50)