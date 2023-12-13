from datetime import date

from django.contrib import auth
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Count, Exists, F, functions, OuterRef, Sum, Q

from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from nutrition.models import User, Unit, Nutrient, ServingSize, Item, CombinedItem, Consumed, CombinedItemElement, ItemNutrient, ItemBioactive, FavoriteItem, GoalTemplate, GoalTemplateNutrient, UserGoal, UserGoalNutrient
from nutrition.utils.nutrition_utils import calculateCalories, calculateMacronutrients, serializeNutrients

from . import permissions, serializers


class UserCreateView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = [AllowAny]

    def create(self, request):
        # Validate data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Validate and hash the password
        password = serializer.validated_data.get('password')
        try:
            auth.password_validation.validate_password(password)
        except DjangoValidationError as error:
            return Response({"password": error.messages}, status=status.HTTP_400_BAD_REQUEST)
        hash = auth.hashers.make_password(password)
        serializer.validated_data['password'] = hash

        # If the data and password are valid, create the user
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserRetrieveUpdateView(RetrieveUpdateAPIView):
    serializer_class = serializers.UserRetrieveUpdateSerializer
    queryset = User.objects.all()

    def get_object(self):
        # Return the currently authenticated user data
        return self.request.user

    def update(self, request):
        # Get authenticated user
        user = self.request.user

        # # Validate data
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        # Make the update
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class ChangePasswordView(APIView):

    def post(self, request):  # Don't remove 'request'
        # Validate data
        serializer = serializers.ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get authenticated user
        user = self.request.user

        # Check if old password is correct
        if user.check_password(serializer.data.get('old_password')):
            # Check if new password meets Django password rules
            password = serializer.data.get('new_password')
            try:
                auth.password_validation.validate_password(password)
            except DjangoValidationError as error:
                return Response({"new_password": error.messages}, status=status.HTTP_400_BAD_REQUEST)
            
            # Set the new user password
            user.set_password(password)
            user.save()

            return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)
        
        return Response({'error': 'Old password entered incorrectly'}, status=status.HTTP_400_BAD_REQUEST)


class UserGoalGenerateView(CreateAPIView):
    serializer_class = serializers.UserGoalSerializer
    queryset = UserGoal.objects.all()

    def create(self, request):
        # Get authenticated user
        user = self.request.user

        # Use the user's info or default values for these attributes
        sex = user.sex or 'Male'
        age = user.age or 30
        isPregnant = user.is_pregnant or False
        isLactating = user.is_lactating or False

        # Get the template that matches the user's info
        template = GoalTemplate.objects.filter(sex=sex, isPregnant=isPregnant, isLactating=isLactating, ageMin__lte=age, ageMax__gte=age).first()
        if not template:
            return Response({'detail': 'No goal templates fit this user'}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate calorie target
        if user.age and user.weight and user.height and user.sex and user.activity_level:
            calories = calculateCalories(user)
        else:
            calories = 2000
        
        # Calculate targets for the macronutrients
        macronutrients = calculateMacronutrients(calories, age)

        # If the user hasn't given their sex, look for an existing goal with a name that is either the same as the template or "Nutritional Goal"
        # If no such goal exists, create it
        goal, created = UserGoal.objects.get_or_create(user=user, name=(template.name if user.sex else 'Nutritional Goal'), defaults={'template': template, 'calories': calories})

        # If the goal was not created because it already exists, update it
        if not created:
            goal.template = template
            goal.calories = calories
            goal.save()

        # Add new UserGoalNutrients for each GoalTemplateNutrient from the the GoalTemplate, setting the goal target values equal to the template recommended values
        templateNutrients = template.goaltemplatenutrient_set.all()
        for nutrient in templateNutrients:
            goalNutrient, created = UserGoalNutrient.objects.get_or_create(goal=goal, nutrient=nutrient.nutrient, defaults={'targetValue': nutrient.recommendedValue})

            # If the nutrient was not created because it already exists, update its targetValue
            if not created:
                goalNutrient.targetValue = nutrient.recommendedValue
                goalNutrient.save()

        # Add a new goal nutrient for each of the three macronutrients
        for nutrientName, targetValue in macronutrients.items():
            nutrient = Nutrient.objects.get_or_create(name=nutrientName)[0]
            goalNutrient, created = UserGoalNutrient.objects.get_or_create(goal=goal, nutrient=nutrient, defaults={'targetValue': targetValue})

            # If the goal nutrient was not created (that is, it already exists), update the targetValue for that macronutrient
            if not created:
                goalNutrient.targetValue = targetValue
                goalNutrient.save()

        # Serialize the new goal
        serializer = self.get_serializer(goal)
        response = serializer.data

        # Format the nutrients and add them to the response
        response["nutrients"] = serializeNutrients(goal)

        return Response(response, status=status.HTTP_201_CREATED)


class UserGoalRetrieveUpdateView(RetrieveUpdateAPIView):
    queryset = UserGoal.objects.all()
    serializer_class = serializers.UserGoalSerializer

    def retrieve(self, request, pk):
        # Get the goal and serialize the data
        goal = UserGoal.objects.filter(id=pk).first()

        # Verify goal exists
        if not goal:
            return Response({'message': 'Requested goal does not exist'}, status=status.HTTP_404_NOT_FOUND)

        # Verify authenticated user matches goal user
        if self.request.user != goal.user:
            return Response({'message': 'Requested goal does not belong to this user'}, status=status.HTTP_403_FORBIDDEN)

        # Serialize the goal and add nutrients
        serializer = self.get_serializer(goal).data
        serializer["nutrients"] = serializeNutrients(goal)

        return Response(serializer, status=status.HTTP_200_OK)

    def update(self, request, pk):
        # Get the goal and user
        goal = UserGoal.objects.filter(id=pk).first()
        user = self.request.user

        # Verify goal exists
        if not goal:
            return Response({'message': 'Requested goal does not exist'}, status=status.HTTP_404_NOT_FOUND)

        # Verify authenticated user matches goal user
        if user != goal.user:
            return Response({'message': 'Requested goal does not belong to this user'}, status=status.HTTP_403_FORBIDDEN)

        # Validate the data using validate function in serializer
        serializer = self.get_serializer(goal, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        # Update 'name' field if it's in the request data
        if 'name' in request.data:
            goal.name = request.data['name']

        # Update 'calories'
        if 'calories' in request.data:
            calories = request.data['calories']
            goal.calories = calories

            # If user age is defined, update the macronutrient distribution based on the new calories
            if user.age:
                macronutrients = calculateMacronutrients(calories, user.age)
                for nutrientName, targetValue in macronutrients.items():
                    nutrient = Nutrient.objects.get_or_create(name=nutrientName)[0] # [0] prevents return of boolean
                    goalNutrient, created = UserGoalNutrient.objects.get_or_create(goal=goal, nutrient=nutrient, defaults={'targetValue': targetValue})

                    # If the UserGoalNutrient was not created (i.e., already exists), update the targetValue
                    if not created:
                        goalNutrient.targetValue = targetValue
                        goalNutrient.save()

        if 'isActive' in request.data:
            # Check if this goal is being set as the active goal
            if request.data['isActive']:
                # Activate this goal and deactivate all other goals
                user.usergoal_set.exclude(pk=goal.pk).update(isActive=False)
                goal.isActive = True
                goal.save()
            else: # If the goal is being deactivated, do not deactivate
                raise ValidationError("To deactivate this goal, set another goal as active")

        # Save the updated goal
        goal.save()

        # Format and add the goal with its nutrients to the response
        response = serializer.data
        response["nutrients"] = serializeNutrients(goal)

        return Response(response, status=status.HTTP_200_OK)


class UserGoalIDListView(ListAPIView):
    serializer_class = serializers.UserGoalIDSerializer

    # Retrieve a list of the user's goals
    def get_queryset(self):
        goals = self.request.user.usergoal_set.all()

        if not goals:
            raise NotFound('No goals found')

        return goals


class UserActiveGoalIDView(RetrieveAPIView):
    serializer_class = serializers.UserGoalIDSerializer

    # Retrieve the user's active goal ID
    def get_object(self):
        activeGoal = self.request.user.usergoal_set.filter(isActive=True).first()

        if not activeGoal:
            raise NotFound('No active goal found')

        return activeGoal


class GoalNutrientStatusView(APIView):

    def get(self, request):  # Don't remove 'request'
        # Get authenticated user and their active goal
        user = self.request.user
        activeGoal = user.usergoal_set.filter(isActive=True).first()

        if not activeGoal:
            return Response({'message': 'No active goal found'}, status=status.HTTP_404_NOT_FOUND)

        # Make a list of all the nutrients in the active goal
        goalNutrients = activeGoal.usergoalnutrient_set.all()
        
        # Get everything the user ate today and separate into list of items and combined items
        consumed = user.consumed_set.filter(consumedAt__date=date.today())
        consumedItems = consumed.filter(item__isnull=False)
        consumedCombinedItems = consumed.filter(combinedItem__isnull=False)
        
        # Calculate how many calories have been consumed in items and combined items
        caloriesConsumedItems = consumedItems.aggregate(totalCalories=Sum(F('item__calories') * F('portion')))['totalCalories'] or 0
        caloriesConsumedCombinedItems = consumedCombinedItems.aggregate(totalCalories=Sum(F('combinedItem__combineditemelement__item__calories') * F('portion')))['totalCalories'] or 0

        # Create a list to hold the status of each nutrient and add calories
        nutrientStatus = [
            {
                "nutrient_id": -1,  # Arbitrary ID for calories
                "nutrient_name": "Calories",
                "nutrient_unit": "kcal",
                "target_value": activeGoal.calories,
                "total_consumed": caloriesConsumedItems + caloriesConsumedCombinedItems,
            }
        ]

        for goalNutrient in goalNutrients:
            # Make a list of of consumed items and combined items that contain the current goal nutrient
            itemsWithNutrient = consumedItems.filter(item__itemnutrient__nutrient=goalNutrient.nutrient)
            combindItemsWithNutrient = consumedCombinedItems.filter(combinedItem__combineditemelement__item__itemnutrient__nutrient=goalNutrient.nutrient)

            # Calculate how much of the current nutrient has been consumed in items and combined items
            nutrientConsumedItems = itemsWithNutrient.aggregate(totalNutrient=Sum(F('portion') * F('item__itemnutrient__amount')))['totalNutrient'] or 0
            nutrientConsumedCombinedItems = combindItemsWithNutrient.aggregate(totalNutrient=Sum(F('portion') * F('combinedItem__combineditemelement__item__itemnutrient__amount')))['totalNutrient'] or 0

            # Add the status of the current nutrient to the status list
            nutrientStatus.append({
                "nutrient_id": goalNutrient.nutrient.id,
                "nutrient_name": goalNutrient.nutrient.name,
                "nutrient_unit": goalNutrient.nutrient.unit.abbreviation,
                "target_value": goalNutrient.targetValue,
                "total_consumed": nutrientConsumedItems + nutrientConsumedCombinedItems,
            })

        # Serialize the list of nutrient statuses
        serializer = serializers.NutrientStatusSerializer(nutrientStatus, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class ConsumedCreateView(CreateAPIView):
    serializer_class = serializers.ConsumedCreateSerializer

    def create(self, request):
        # Validate the data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # If data is valid, create consumed item for authenticated user
        serializer.save(user=self.request.user)

        return Response({'message': 'Consumption recorded successfully'}, status=status.HTTP_201_CREATED)


class UserConsumedItemsView(APIView):

    def get(self, request): # Don't remove 'request'
        # Get all items consumed on current date by authenticated user
        consumedItems = self.request.user.consumed_set.filter(consumedAt__date=date.today())

        # Create a list to store serialized consumed items
        consumedItemsList = []

        # Serialize the consumed items
        for consumedItem in consumedItems:
            if consumedItem.item:
                consumedItemsList.append({
                    "id": consumedItem.id,
                    "item_id": consumedItem.item.id,
                    "type": "Item",
                    "name": consumedItem.item.name,
                    "portion": consumedItem.portion,
                })
            elif consumedItem.combinedItem:
                consumedItemsList.append({
                    "id": consumedItem.id,
                    "item_id": consumedItem.combinedItem.id,
                    "type": "CombinedItem",
                    "name": consumedItem.combinedItem.name,
                    "portion": consumedItem.portion,
                })

        return Response(consumedItemsList, status=status.HTTP_200_OK)


class ToggleFavoriteView(APIView):
    queryset = FavoriteItem.objects.all()
    serializer_class = serializers.FavoriteItemSerializer

    def post(self, request, item_id): # Don't remove 'request'
        # Verify item exists
        item = Item.objects.filter(id=item_id).first()
        if not item:
            return Response({'message': 'Item does not exist'}, status=status.HTTP_404_NOT_FOUND)

        # Try to mark the item as a favorite of the authenticated user by creating a favoriteItem object
        favoriteItem, created = FavoriteItem.objects.get_or_create(user=self.request.user, item=item)

        # If the favoriteItem was created, the item is now marked as a favorite, otherwise delete the favoriteItem to unfavorite the item
        if created:
            return Response({'message': 'Item favorited'}, status=status.HTTP_201_CREATED)
        else:
            favoriteItem.delete()
            return Response({'message': 'Item unfavorited'}, status=status.HTTP_200_OK)


class FavoriteItemIDListView(ListAPIView):
    serializer_class = serializers.FavoriteItemIDSerializer

    # Retrieve a list of the authenticated user's favorites
    def get_queryset(self):
        favorites = self.request.user.favoriteitem_set.all()

        if not favorites:
            raise NotFound('No favorites found')

        return favorites

class ItemCreateView(CreateAPIView):
    serializer_class = serializers.ItemCreateSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Create the item
        item = Item.objects.create(
            name=serializer.data['name'],
            calories=serializer.validated_data['calories'],
            servingSize=ServingSize.objects.create(amount=serializer.validated_data['serving_amount'], unit=serializer.validated_data['serving_unit']),
            user=self.request.user,
            isCustom=True
        )

        # Add each of the item's nutrients
        createdNutrients = []
        for id, amount in serializer.data['nutrients'].items():
            # Verify nutrient exists
            nutrientToAdd = Nutrient.objects.filter(id=id).first()
            if not nutrientToAdd:
                return Response({'error': 'Nutrient does not exist'}, status=status.HTTP_404_NOT_FOUND)
            
            # Link the item and the nutrient
            itemNutrient = ItemNutrient.objects.create(item=item, nutrient=nutrientToAdd, amount=amount)
            nutrientData = {
                'id': nutrientToAdd.id,
                'name': nutrientToAdd.name,
                'unit': nutrientToAdd.unit.abbreviation,
                'amount': itemNutrient.amount
            }
            createdNutrients.append(nutrientData)

        # Prepare the response
        createdItem = serializers.ItemSerializer(item)
        itemAndNutrients = {
            'item': createdItem.data,
            'nutrients': createdNutrients
        }

        return Response(itemAndNutrients, status=status.HTTP_201_CREATED)

 
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = serializers.UserSerializer
    permission_classes = [IsAdminUser]

class GroupViewSet(viewsets.ModelViewSet):
    queryset = auth.models.Group.objects.all()
    serializer_class = serializers.GroupSerializer
    permission_classes = [IsAdminUser]

class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.all()
    serializer_class = serializers.UnitSerializer
    permission_classes = [permissions.IsAdminUserOrReadOnly]

class NutrientViewSet(viewsets.ModelViewSet):
    queryset = Nutrient.objects.all()
    serializer_class = serializers.NutrientSerializer
    permission_classes = [permissions.IsAdminUserOrReadOnly]

class ServingSizeViewSet(viewsets.ModelViewSet):
    queryset = ServingSize.objects.all()
    serializer_class = serializers.ServingSizeSerializer
    permission_classes = [IsAuthenticated]

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = serializers.ItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        barcode = self.request.query_params.get('barcode', None)
        name = self.request.query_params.get('name', None)
        # Check if request contains barcode
        if barcode is not None:
            queryset = queryset.filter(barcode=barcode)
            # Verify an item with the barcode exists
            if not queryset.exists():
                raise NotFound('No items match this barcode')
        # Check if request contains name
        elif name is not None:
            words = name.split()
            for word in words:
                queryset = queryset.filter(name__icontains=word)
            # Verify an item containing the name exists
            if not queryset.exists():
                raise NotFound('No matching items')
            queryset = queryset.annotate(nameLength=functions.Length('name'), nutrientCount=Count('nutrients')).order_by('nameLength', '-nutrientCount')[:10]

        queryset = queryset.annotate(isFavorite=Exists(FavoriteItem.objects.filter(user=user, item=OuterRef('id'))))

        return queryset

class CombinedItemViewSet(viewsets.ModelViewSet):
    queryset = CombinedItem.objects.all()
    serializer_class = serializers.CombinedItemSerializer
    permission_classes = [IsAuthenticated]

class ConsumedViewSet(viewsets.ModelViewSet):
    queryset = Consumed.objects.all()
    serializer_class = serializers.ConsumedSerializer
    permission_classes = [IsAuthenticated]

class CombinedItemElementViewSet(viewsets.ModelViewSet):
    queryset = CombinedItemElement.objects.all()
    serializer_class = serializers.CombinedItemElementSerializer
    permission_classes = [IsAuthenticated]

class ItemNutrientViewSet(viewsets.ModelViewSet):
    queryset = ItemNutrient.objects.all()
    serializer_class = serializers.ItemNutrientSerializer
    permission_classes = [IsAuthenticated]

class ItemBioactiveViewSet(viewsets.ModelViewSet):
    queryset = ItemBioactive.objects.all()
    serializer_class = serializers.ItemBioactiveSerializer
    permission_classes = [IsAuthenticated]

class FavoriteItemViewSet(viewsets.ModelViewSet):
    queryset = FavoriteItem.objects.all()
    serializer_class = serializers.FavoriteItemSerializer
    permission_classes = [IsAuthenticated]

class GoalTemplateViewSet(viewsets.ModelViewSet):
    queryset = GoalTemplate.objects.all()
    serializer_class = serializers.GoalTemplateSerializer
    permission_classes = [permissions.IsAdminUserOrReadOnly]

class GoalTemplateNutrientViewSet(viewsets.ModelViewSet):
    queryset = GoalTemplateNutrient.objects.all()
    serializer_class = serializers.GoalTemplateNutrientSerializer
    permission_classes = [permissions.IsAdminUserOrReadOnly]

class UserGoalViewSet(viewsets.ModelViewSet):
    queryset = UserGoal.objects.all()
    serializer_class = serializers.UserGoalSerializer
    permission_classes = [IsAuthenticated]

class UserGoalNutrientViewSet(viewsets.ModelViewSet):
    queryset = UserGoalNutrient.objects.all()
    serializer_class = serializers.UserGoalNutrientSerializer
    permission_classes = [IsAuthenticated]