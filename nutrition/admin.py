from django.contrib import admin
from .models import User, Unit, ServingSize, Nutrient, Item, CombinedItem, Consumed, CombinedItemElement, ItemNutrient, ItemBioactive, FavoriteItem, NutritionalGoalTemplate, GoalTemplateNutrient, UserNutritionalGoal, UserNutritionalGoalNutrient

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'age', 'weight', 'height', 'sex', 'is_pregnant', 'is_staff', 'is_superuser', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'date_joined')
    
@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(ServingSize)
class ServingSizeAdmin(admin.ModelAdmin):
    list_display = ('amount', 'unitId')

@admin.register(Nutrient)
class NutrientAdmin(admin.ModelAdmin):
    list_display = ('name', 'unitId', 'isCategory', 'parentNutrientId')


class ItemNutrientInline(admin.TabularInline):
    model = ItemNutrient
    extra = 1

class ItemBioactiveInline(admin.TabularInline):
    model = ItemBioactive
    extra = 1

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'barcode', 'calories', 'servingSizeId', 'userId', 'isCustom')
    list_filter = ('isCustom',)
    inlines = [ItemNutrientInline, ItemBioactiveInline]
    
@admin.register(CombinedItem)
class CombinedItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'userId')

@admin.register(Consumed)
class ConsumedAdmin(admin.ModelAdmin):
    list_display = ('userId', 'item_display', 'combined_item_display', 'consumedAt', 'portion')
    list_filter = ('userId', 'consumedAt')

    def item_display(self, obj):
        return obj.itemId.name if obj.itemId else ''
    item_display.short_description = 'Item'

    def combined_item_display(self, obj):
        return obj.combinedItemId.name if obj.combinedItemId else ''
    combined_item_display.short_description = 'Combined Item'

@admin.register(CombinedItemElement)
class CombinedItemElementAdmin(admin.ModelAdmin):
    list_display = ('combinedItemId', 'itemId', 'portion')

@admin.register(FavoriteItem)
class FavoriteItemAdmin(admin.ModelAdmin):
    list_display = ('userId', 'itemId')

class GoalTemplateNutrientInline(admin.TabularInline):
    model = GoalTemplateNutrient
    extra = 1

@admin.register(NutritionalGoalTemplate)
class NutritionalGoalTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'calories')
    inlines = [GoalTemplateNutrientInline]

@admin.register(GoalTemplateNutrient)
class GoalTemplateNutrientAdmin(admin.ModelAdmin):
    list_display = ('templateId', 'nutrientId', 'recommendedValue')

class UserNutritionalGoalNutrientInline(admin.TabularInline):
    model = UserNutritionalGoalNutrient
    extra = 1

@admin.register(UserNutritionalGoal)
class UserNutritionalGoalAdmin(admin.ModelAdmin):
    list_display = ('userId', 'name', 'templateId', 'calories')
    inlines = [UserNutritionalGoalNutrientInline]

@admin.register(UserNutritionalGoalNutrient)
class UserNutritionalGoalNutrientAdmin(admin.ModelAdmin):
    list_display = ('goalId', 'nutrientId', 'recommendedValue')
