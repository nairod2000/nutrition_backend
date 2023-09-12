from django.contrib import admin
from django.contrib.auth.models import User
from .models import Unit, FoodItem, Supplement, Vitamin, Mineral, CombinedItem, Consumed, CombinedItemElement, FoodVitamin, FoodMineral, SupplementVitamin, SupplementMineral, SupplementIngredient

class FoodVitaminInline(admin.StackedInline):
    model = FoodVitamin

class FoodMineralInline(admin.StackedInline):
    model = FoodMineral

class SupplementVitaminInline(admin.StackedInline):
    model = SupplementVitamin

class SupplementMineralInline(admin.StackedInline):
    model = SupplementMineral

class SupplementIngredientInline(admin.StackedInline):
    model = SupplementIngredient

class CombinedItemElementInline(admin.StackedInline):
    model = CombinedItemElement

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'barcode', 'calories', 'protein', 'carbs', 'fats', 'unit', 'servingSize')
    inlines = [FoodVitaminInline, FoodMineralInline]

@admin.register(Supplement)
class SupplementAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'barcode')
    inlines = [SupplementVitaminInline, SupplementMineralInline, SupplementIngredientInline]

@admin.register(Vitamin)
class VitaminAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'unit')

@admin.register(Mineral)
class MineralAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'unit')

@admin.register(CombinedItem)
class CombinedItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'userId', 'name')
    inlines = [CombinedItemElementInline]

@admin.register(Consumed)
class ConsumedAdmin(admin.ModelAdmin):
    list_display = ('id', 'userId', 'foodId', 'supplementId', 'combinedItemId', 'consumedAt', 'portion')

@admin.register(CombinedItemElement)
class CombinedFoodElementAdmin(admin.ModelAdmin):
    list_display = ('id', 'combinedFoodId', 'foodId', 'servingSize')

@admin.register(FoodVitamin)
class FoodVitaminAdmin(admin.ModelAdmin):
    list_display = ('id', 'foodId', 'vitaminId', 'amount')

@admin.register(FoodMineral)
class FoodMineralAdmin(admin.ModelAdmin):
    list_display = ('id', 'foodId', 'mineralId', 'amount')

@admin.register(SupplementVitamin)
class SupplementVitaminAdmin(admin.ModelAdmin):
    list_display = ('id', 'supplementId', 'vitaminId', 'amount')

@admin.register(SupplementMineral)
class SupplementMineralAdmin(admin.ModelAdmin):
    list_display = ('id', 'supplementId', 'mineralId', 'amount')

@admin.register(SupplementIngredient)
class SupplementIngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'supplementId', 'foodId', 'amount', 'unit')
