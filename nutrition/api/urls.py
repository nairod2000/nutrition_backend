from django.urls import include, path
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token
from . import views

# Automatic URL routing for ViewSets
router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'units', views.UnitViewSet)
router.register(r'nutrients', views.NutrientViewSet)
router.register(r'servingsizes', views.ServingSizeViewSet)
router.register(r'items', views.ItemViewSet)
router.register(r'combineditems', views.CombinedItemViewSet)
router.register(r'consumeditems', views.ConsumedViewSet)
router.register(r'combineditemelements', views.CombinedItemElementViewSet)
router.register(r'itemnutrients', views.ItemNutrientViewSet)
router.register(r'itembioactives', views.ItemBioactiveViewSet)
router.register(r'favoriteitems', views.FavoriteItemViewSet)
router.register(r'goaltemplates', views.GoalTemplateViewSet)
router.register(r'goaltemplatenutrients', views.GoalTemplateNutrientViewSet)
router.register(r'usergoals', views.UserGoalViewSet)
router.register(r'usergoalnutrients', views.UserGoalNutrientViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api-token-auth/', obtain_auth_token),
    path('user-create/', views.UserCreateView.as_view(), name='user_create'),
    path('user/', views.UserRetrieveUpdateView.as_view(), name='user_update'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('goal-generate/', views.UserGoalGenerateView.as_view(), name='goal-generate'),
    path('goal/<int:pk>/', views.UserGoalRetrieveUpdateView.as_view(), name='goal-update'),
    path('user-goals/', views.UserGoalsListView.as_view(), name='user-goals'),
    path('active-goal/', views.UserActiveGoalView.as_view(), name='active-goal'),
    path('goal-nutrient-status/', views.GoalNutrientStatusView.as_view(), name='goal-nutrient-status'),
]
