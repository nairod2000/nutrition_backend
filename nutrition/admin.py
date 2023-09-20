from django.contrib import admin
from .models import Users
from .models import FoodItem
from .models import Supplement
from .models import Vitamin
from .models import Mineral
from .models import CombinedItem
from .models import Consumed
from .models import CombinedFoodElement
from .models import FoodVitamin
from .models import FoodMineral
from .models import SupplementVitamin
from .models import SupplementMineral


# Register your models here.
admin.site.register(Users)
admin.site.register(FoodItem)
admin.site.register(Supplement)
admin.site.register(Vitamin)
admin.site.register(Mineral)
admin.site.register(CombinedItem)
admin.site.register(Consumed)
admin.site.register(CombinedFoodElement)
admin.site.register(FoodVitamin)
admin.site.register(FoodMineral)
admin.site.register(SupplementVitamin)
admin.site.register(SupplementMineral)