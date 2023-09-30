from django.contrib import admin
from .models import User, Unit, ServingSize, Nutrient, Item, CombinedItem, Consumed, CombinedItemElement, ItemNutrient, ItemBioactive, FavoriteItem, GoalTemplate, GoalTemplateNutrient, UserGoal, UserGoalNutrient


class FavoriteItemInline(admin.TabularInline):
    model = FavoriteItem

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'age', 'weight', 'height', 'sex', 'is_pregnant', 'is_staff', 'is_superuser', 'date_joined', 'favorites')
    list_filter = ('is_staff', 'is_superuser', 'date_joined')
    inlines = [FavoriteItemInline]
    
@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(ServingSize)
class ServingSizeAdmin(admin.ModelAdmin):
    list_display = ('amount', 'unit')

@admin.register(Nutrient)
class NutrientAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit', 'isCategory', 'parentNutrient')

class ItemNutrientInline(admin.TabularInline):
    model = ItemNutrient

class ItemBioactiveInline(admin.TabularInline):
    model = ItemBioactive

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'barcode', 'calories', 'servingSize', 'user', 'isCustom')
    list_filter = ('isCustom',)
    inlines = [ItemNutrientInline, ItemBioactiveInline]
    
@admin.register(CombinedItem)
class CombinedItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'user')

@admin.register(Consumed)
class ConsumedAdmin(admin.ModelAdmin):
    list_display = ('user', 'item_display', 'combined_item_display', 'consumedAt', 'portion')
    list_filter = ('user', 'consumedAt')

    def item_display(self, obj):
        return obj.item.name if obj.item else ''
    item_display.short_description = 'Item'

    def combined_item_display(self, obj):
        return obj.combinedItem.name if obj.combinedItem else ''
    combined_item_display.short_description = 'Combined Item'

@admin.register(CombinedItemElement)
class CombinedItemElementAdmin(admin.ModelAdmin):
    list_display = ('combinedItem', 'item', 'portion')

@admin.register(FavoriteItem)
class FavoriteItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'item')

class GoalTemplateNutrientInline(admin.TabularInline):
    model = GoalTemplateNutrient

@admin.register(GoalTemplate)
class GoalTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'calories')
    inlines = [GoalTemplateNutrientInline]

@admin.register(GoalTemplateNutrient)
class GoalTemplateNutrientAdmin(admin.ModelAdmin):
    list_display = ('template', 'nutrient', 'recommendedValue')

class UserGoalNutrientInline(admin.TabularInline):
    model = UserGoalNutrient

@admin.register(UserGoal)
class UserGoalAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'template', 'calories')
    inlines = [UserGoalNutrientInline]

@admin.register(UserGoalNutrient)
class UserGoalNutrientAdmin(admin.ModelAdmin):
    list_display = ('goal', 'nutrient', 'recommendedValue')
