from django.contrib import admin
from .models import User, Unit, Nutrient, Item, ServingSize, CombinedItem, Consumed, CombinedItemElement, ItemNutrient, ItemBioactive, NutritionalGoalTemplate, GoalTemplateNutrient, UserNutritionalGoal, UserNutritionalGoalNutrient

class ItemNutrientInline(admin.TabularInline):
    model = ItemNutrient

class ItemBioactiveInline(admin.TabularInline):
    model = ItemBioactive

class CombinedItemElementInline(admin.TabularInline):
    model = CombinedItemElement

class ConsumedInline(admin.TabularInline):
    model = Consumed

@admin.register(User)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'age', 'weight', 'height', 'sex', 'is_pregnant', 'is_staff', 'is_superuser')

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

@admin.register(ServingSize)
class ServingSizeAdmin(admin.ModelAdmin):
    list_display = ('id', 'amount', 'unit')

@admin.register(Nutrient)
class NutrientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'unit', 'isCategory', 'parentNutrient')

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'barcode', 'servingSize')
    inlines = [ItemNutrientInline, ItemBioactiveInline]

@admin.register(CombinedItem)
class CombinedItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'userId', 'name')
    inlines = [CombinedItemElementInline]

@admin.register(Consumed)
class ConsumedAdmin(admin.ModelAdmin):
    list_display = ('id', 'userId', 'itemId', 'combinedItemId', 'consumedAt', 'portion')

@admin.register(CombinedItemElement)
class CombinedItemElementAdmin(admin.ModelAdmin):
    list_display = ('id', 'combinedItemId', 'itemId', 'portion')

@admin.register(ItemNutrient)
class ItemNutrientAdmin(admin.ModelAdmin):
    list_display = ('id', 'itemId', 'nutrientId', 'amount')

@admin.register(ItemBioactive)
class ItemBioactiveAdmin(admin.ModelAdmin):
    list_display = ('id', 'itemId', 'name', 'amount', 'unit')

@admin.register(NutritionalGoalTemplate)
class NutritionalGoalTemplateAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

@admin.register(GoalTemplateNutrient)
class GoalTemplateNutrientAdmin(admin.ModelAdmin):
    list_display = ('id', 'nutrient', 'template', 'recommendedValue')

@admin.register(UserNutritionalGoal)
class UserNutritionalGoalAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'template')

@admin.register(UserNutritionalGoalNutrient)
class UserNutritionalGoalNutrientAdmin(admin.ModelAdmin):
    list_display = ('id', 'goal', 'nutrient', 'recommendedValue')
