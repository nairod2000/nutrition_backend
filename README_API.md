# Nutrition API Documentation

## Request Headers

Headers required for all requests (unless noted differently):
`Content-Type: application/json`
`Authorization: Token user_token`

## Token Authentication

This endpoint generates a user authentication token that can be used in other request headers.

- **Endpoint:** `/api/api-token-auth/`

**Request:**
```
POST
(No Authorization header needed)
{
    "username": "Username",
    "password": "Password"
}
```

**Response:**
```
{
    "token": "user_token"
}
```


## User Management

### Create a User (Sign Up)

- **Endpoint:** `/api/user-create/`

**Request:**
```
POST
(No Authorization header needed)
{
    "is_superuser": false,
    "username": "Username",
    "password": "Password",
    "first_name": "FirstName",
    "last_name": "LastName",
    "email": "user@example.com",
    "is_staff": false,
    "age": 30, // in years
    "weight": 180, // in pounds
    "height": 64, // in inches
    "sex": "Male", // Valid choices: "Male", "Female"
    "is_pregnant": false,
    "is_lactating": false,
    "activity_level": "Lightly Active", // Valid choices: "Sedentary", "Lightly Active", "Moderately Active", "Very Active", "Extremely Active"
    "diet_goal": "Lose Weight" // Valid choices: "Lose Weight", "Maintain Weight", and "Gain Weight"
}
```
Notes for request:
 - You must include `username` and `password`, but everything else is optional.
 - Valid choices noted in comments are case sensitive

**Response:**
```
{
    "id": 3,
    "last_login": null,
    "is_superuser": false,
    "username": "Username",
    "first_name": "FirstName",
    "last_name": "LastName",
    "email": "user@example.com",
    "is_staff": false,
    "is_active": true,
    "date_joined": "2023-09-21T18:37:29.183846-05:00",
    "age": 30, // in years
    "weight": 180, // in pounds
    "height": 64, // in inches
    "sex": "Male",
    "is_pregnant": false,
    "is_lactating": false,
    "groups": [],
    "user_permissions": []
}
```

### Retrieve and Update User Profile

- **Endpoint:** `/api/user/`
- **Methods:** GET (retrieve), PUT or PATCH (update)

**Request (Retrieve):**
```
GET
(Leave request body blank)
```

**Response (Retrieve):**
```
{
    "username": "Username",
    "email": "user@example.com",
    "first_name": "FirstName",
    "last_name": "LastName",
    "age": 30, // in years
    "weight": 180, // in pounds
    "height": 64, // in inches
    "sex": Male,
    "is_pregnant": false,
    "is_lactating": false,
    "activity_level": "Lightly Active",
    "diet_goal": "Lose Weight"
}
```

**Request (Full or Partial Update):**
```
PUT or PATCH
{
    "username": "Username",
    "email": "user@example.com",
    "first_name": "FirstName",
    "last_name": "LastName"
    "age": 30, // in years
    "weight": 180, // in pounds
    "height": 64, // in inches
    "sex": "Male", // Valid choices: "Male", "Female"
    "is_pregnant": false,
    "is_lactating": false,
    "activity_level": "Lightly Active", // Valid choices: "Sedentary", "Lightly Active", "Moderately Active", "Very Active", "Extremely Active"
    "diet_goal": "Lose Weight" // Valid choices: "Lose Weight", "Maintain Weight", and "Gain Weight"
}
```
Notes for request:
 - All fields are optional in PUT and PATCH requests. The request will work like a GET request if all fields are left out.
 - Valid choices noted in comments are case sensitive

**Response (Full or Partial Update):**
```
{
    "username": "Username",
    "email": "user@example.com",
    "first_name": "FirstName",
    "last_name": "LastName"
    "age": 30, // in years
    "weight": 180, // in pounds
    "height": 64, // in inches
    "sex": "Male",
    "is_pregnant": false,
    "is_lactating": false,
    "activity_level": "Lightly Active",
    "diet_goal": "Lose Weight"
}
```

### Change Password

- **Endpoint:** `/api/change-password/`

**Request:**
```
POST
{
    "old_password": "OldPassword",
    "new_password": "NewPassword"
}
```

**Response:**
```
{
    "message": "Password changed successfully"
}
```

## User Goal Management

### Generate User Goal

- **Endpoint:** `/api/goal-generate/`

This endpoint uses the attributes of a user to generate and return the details of a nutrition goal, specifically calorie and nutrient tartets.

The calorie target is computed using a process built on the Mifflin-St Jeor Equation. The calculation depends on the user’s age, weight, height, sex, activity level, diet goal, and whether the user is pregnant or lactating. `is_pregnant` and `is_lactating` will default to `false` and `diet_goal` will default to 'Maintain Weight' if they aren't defined. (This won't modify the actual user attributes.) If `age`, `weight`, `height`, `sex`, or `activity_level` aren’t defined, the calorie target will default to 2000 calories.

The targets for the macronutrients Carbohydrate, Fat, and Protein are calculated by dividing the calculated calorie target among them based the user age and FDA recommendations based on age. `age` will default 30 if it isn't defined. (This doesn't modify the actual user age.)
 
Micronutrient targets are determined using FDA recommendations which are based on sex, age, and whether pregnant or lactating. `sex` defaults to 'Male', `age` defaults to 30, and `is_pregnant` and `is_lactating` default to `false` if they aren't defined. (This doesn't modify the actual user attributes.)

If the user attribute `sex` isn’t defined, the `name` attribute of the new goal will default to 'Nutritional Goal'. Otherwise, it will be based on the same user attributes that were used to select which GoalTemplate would used to set the micronutrient targets. If there already exists a goal with the same name, a request will update the attributes of the existing goal instead of generating a new one.

**Request:**
```
POST
(Leave request body blank)
```

**Response:**
```
{
    "id": 10,
    "name": "FDA RDIs for Males Ages 31 to 50",
    "calories": "2500",
    "isActive": true,
    "user": 1,
    "template": 15,
    "nutrients": [
        {
            "id": 100,
            "nutrient": {
                "id": 20,
                "name": "Protein",
                "unit": g
            },
            "targetValue": 80
        },
        {
            "id": 101,
            "nutrient": {
                "id": 21,
                "name": "Vitamin C",
                "unit": mg
            },
            "targetValue": 1000
        },
        // Other UserGoalNutrient objects here
    ]
}
```


### Retrieve or Update User Goal

- **Endpoint:** `/api/goal/{goal_id}/`
- **Methods:** GET (retrieve), PUT or PATCH (update)

**Request (Update):**
```
PUT
{
    "name": "New Goal Name",
    "calories": 2000, // Updating calories will update target values for Carbohydrate, Fat, and Protein
    "isActive": true,
    // To update individual goal nutrients, use the endpoint /api/usergoalnutrients/{id}/
}
```
Note for request:
 - The `user` and `template` fields cannot be modified.
 - The `nutrients` field is read-only. To update individual goal nutrients, use the endpoint `/api/usergoalnutrients/{id}/`.
 - To ensure one and only one goal is active for each user, the `isActive` field can only be set to `true`, and doing so will deactivate all other goals for that user. To deactivate an active goal, set `isActive` to `true` for one of the user’s other goals.
 

**Response (Retrieve or Update):**
```
{
    "id": 10,
    "name": "FDA RDIs for Males Ages 31 to 50",
    "calories": "2500",
    "isActive": true,
    "user": 1,
    "template": 15,
    "nutrients": [
        {
            "id": 100,
            "nutrient": {
                "id": 20,
                "name": "Protein",
                "unit": g
            },
            "targetValue": 80
        },
        {
            "id": 101,
            "nutrient": {
                "id": 21,
                "name": "Vitamin C",
                "unit": mg
            },
            "targetValue": 1000
        },
        // Other UserGoalNutrient objects here
    ]
}
```

### Retrieve List of User's Goal IDs

- **Endpoint:** `/api/user-goals/`

**Request:**
```
GET
(Leave request body blank)
```

**Response:**
```
{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 15
        },
        {
            "id": 17
        }
    ]
}
```
If the response contains enough items to require pagination, "next" and "previous" in the response indicate the URL for the next or subsequent page of results. Otherwise, they are set to null.


### Retrieve User's Active Goal ID

- **Endpoint:** `/api/active-goal/`

**Request:**
```
GET
(Leave request body blank)
```

**Response:**
```
{
    "id": 10
}
```


## Summary Statistics

### User's Goal Nutrient Status

This endpoint returns details about the status of the user’s nutrient consumption on the current day compared to the user's active goal. It calculates the total consumption for every nutrient contained in the active goal based on the items and combined items that the user has recorded as consumed on the current date.

- **Endpoint:** `/api/goal-nutrient-status/`

**Request:**
```
GET
(Leave request body blank)
```

**Response:**
```
[
    {
        "nutrient_id": -1,
        "nutrient_name": "Calories",
        "nutrient_unit": "kcal",
        "target_value": 2000.0,
        "total_consumed": 2050.0
    },
    {
        "nutrient_id": 1,
        "nutrient_name": "Protein",
        "nutrient_unit": "g",
        "target_value": 50.0,
        "total_consumed": 45.0
    },
    {
        "nutrient_id": 2,
        "nutrient_name": "Fat",
        "nutrient_unit": "g",
        "target_value": 70.0,
        "total_consumed": 55.0
    },
    {
        "nutrient_id": 3,
        "nutrient_name": "Carbohydrate",
        "nutrient_unit": "g",
        "target_value": 130.0,
        "total_consumed": 120.0
    },
    // ... (more nutrients)
]
```


## Consumed Items

### Record Item Consumption

- **Endpoint:** `/api/consumed-create/`

**Request:**
```
POST
{
    "item": 3, // Alternatively: "combinedItem": 3
    "portion": 1.75
}
```
Notes for request:
 - Request must include either `item` or `combinedItem` and must not include both.

**Response:**
```
{
    "message": "Consumption recorded successfully"
}
```


### List User's Items Consumed Today

This endpoint returns a list of all items and combined items consumed by the authenticated user on the current date.

- **Endpoint:** `/api/consumed-items/`

**Request:**
```
GET
(Leave request body blank)
```

**Response:**
```
[
    {
        "id": 50,
        "type": "Item",
        "name": "Banana",
        "portion": 2.0
    },
    {
        "id": 200,
        "type": "CombinedItem",
        "name": "Egg and Toast Breakfast",
        "portion": 1.2
    },
    {
        "id": 123,
        "type": "Item",
        "name": "Frozen Pizza",
        "portion": 0.5
    }
]
```


## Items

### Toggle Item as Favorite or Not for User

This endpoint will set a not-favorite item as a favorite or set a favorite item as not-favorite for the authenticated user

- **Endpoint:** `/api/toggle-favorite/{item_id}/`

**Request:**
```
GET
(Leave request body blank; include item id in URL)
```

**Responses:**
```
{
    "message": "Item favorited"
}
```
```
{
    "message": "Item unfavorited"
}
```


### Retrieve List of IDs of User's Favorite Items

- **Endpoint:** `/api/favorites/`

**Request:**
```
GET
(Leave request body blank)
```

**Response:**
```
{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "item": 4
        },
        {
            "item": 8
        }
    ]
}
```
If the response contains enough items to require pagination, "next" and "previous" in the response indicate the URL for the next or subsequent page of results. Otherwise, they are set to null.


### Retrieve Item by Barcode

- **Endpoint:** `/api/items/?barcode={barcode}/`

**Request:**
```
GET
(Leave request body blank; include barcode in URL)
```

**Responses:**
```
{
    "id": 1,
    "name": "Banana",
    "barcode": "123456",
    "calories": 50,
    "isCustom": false,
    "servingSize": 4,
    "user": null,
    "nutrients": [
        2,
        4,
        7,
        8
    ]
}
```


### Create Item With Nutrients

- **Endpoint:** `/api/item-create/`

**Request:**
```
POST
{
    "name": "New Food Item",
    "calories": "100",
    "serving_amount": "10.5",
    "serving_unit": 10,
    "nutrients": {
        "2": "10.5",
        "7": "20.0"
    }
}
```

**Responses:**
```
{
    "item": {
        "id": 204457,
        "name": "New Food Item",
        "barcode": null,
        "calories": 100,
        "servingSize": 206650,
        "isCustom": true,
        "user": 1,
        "nutrients": [
            2,
            7
        ]
    },
    "nutrients": [
        {
            "id": 2,
            "name": "Carbohydrate",
            "unit": "g",
            "amount": "10.50"
        },
        {
            "id": 7,
            "name": "Protein",
            "unit": "g",
            "amount": "20.00"
        }
    ]
}
```


## "Regular" View Set Endpoints

These endpoints are based on the Django REST Framework's ModelViewSet. They offer CRUD operations for each model and access to all model fields. POST, PUT, PATCH, or DELETE requests to some endpoints may be sent only by superusers. The browsable API can be used to find details on available fields. These endpoints can be used via the browsable API at http://localhost:8000/api/ after starting a local server with `python models.py runserver`.


### Users
**Endpoint:** `/api/users/`
- **Methods:**
  - `GET`: Retrieve a list of all users.
  - `POST`: Create a new user.
- **Permissions:** Admin users only for POST.

**Endpoint:** `/api/users/{id}/`
- **Methods:**
  - `GET`: Retrieve a specific user by ID.
  - `PUT/PATCH`: Update a specific user by ID.
  - `DELETE`: Delete a specific user by ID.
- **Permissions:** Admin users only for PUT, PATCH, DELETE.

### Groups
**Endpoint:** `/api/groups/`
- **Methods:** 
  - `GET`: Retrieve a list of all groups.
  - `POST`: Create a new group.
- **Permissions:** Admin users only.

**Endpoint:** `/api/groups/{id}/`
- **Methods:** 
  - `GET`: Retrieve a specific group by ID.
  - `PUT/PATCH`: Update a specific group by ID.
  - `DELETE`: Delete a specific group by ID.
- **Permissions:** Admin users only for PUT, PATCH, DELETE.

### Units
**Endpoint:** `/api/units/`
- **Methods:**
  - `GET`: Retrieve a list of all units.
  - `POST`: Create a new unit.
- **Permissions:** Admin users can modify, read-only for others.

**Endpoint:** `/api/units/{id}/`
- **Methods:**
  - `GET`: Retrieve a specific unit by ID.
  - `PUT/PATCH`: Update a specific unit by ID.
  - `DELETE`: Delete a specific unit by ID.
- **Permissions:** Admin users can modify, read-only for others.

### Nutrients
**Endpoint:** `/api/nutrients/`
- **Methods:**
  - `GET`: Retrieve a list of all nutrients.
  - `POST`: Create a new nutrient.
- **Permissions:** Admin users can modify, read-only for others.

**Endpoint:** `/api/nutrients/{id}/`
- **Methods:**
  - `GET`: Retrieve a specific nutrient by ID.
  - `PUT/PATCH`: Update a specific nutrient by ID.
  - `DELETE`: Delete a specific nutrient by ID.
- **Permissions:** Admin users can modify, read-only for others.

### Serving Sizes
**Endpoint:** `/api/servingsizes/`
- **Methods:**
  - `GET`: Retrieve a list of all serving sizes.
  - `POST`: Create a new serving size.
- **Permissions:** Authenticated users only.

**Endpoint:** `/api/servingsizes/{id}/`
- **Methods:**
  - `GET`: Retrieve a specific serving size by ID.
  - `PUT/PATCH`: Update a specific serving size by ID.
  - `DELETE`: Delete a specific serving size by ID.
- **Permissions:** Authenticated users only.

`/api/servingsizes/{id}/` GET response:

```
{
    "id": 1,
    "amount": "50.00",
    "unit": 3,
    "unit_abbreviation": "g"
}
```

### Items
**Endpoint:** `/api/items/`
- **Methods:**
  - `GET`: Retrieve a list of all items.
  - `POST`: Create a new item.
- **Permissions:** Authenticated users only.

**Endpoint:** `/api/items/{id}/`
- **Methods:**
  - `GET`: Retrieve a specific item by ID.
  - `PUT/PATCH`: Update a specific item by ID.
  - `DELETE`: Delete a specific item by ID.
- **Permissions:** Authenticated users only.

### Combined Items
**Endpoint:** `/api/combineditems/`
- **Methods:**
  - `GET`: Retrieve a list of all combined items.
  - `POST`: Create a new combined item.
- **Permissions:** Authenticated users only.

**Endpoint:** `/api/combineditems/{id}/`
- **Methods:**
  - `GET`: Retrieve a specific combined item by ID.
  - `PUT/PATCH`: Update a specific combined item by ID.
  - `DELETE`: Delete a specific combined item by ID.
- **Permissions:** Authenticated users only.

### Consumed Items
**Endpoint:** `/api/consumeditems/`
- **Methods:**
  - `GET`: Retrieve a list of all consumed items.
  - `POST`: Create a new consumed item.
- **Permissions:** Authenticated users only.

**Endpoint:** `/api/consumeditems/{id}/`
- **Methods:**
  - `GET`: Retrieve a specific consumed item by ID.
  - `PUT/PATCH`: Update a specific consumed item by ID.
  - `DELETE`: Delete a specific consumed item by ID.
- **Permissions:** Authenticated users only.

### Combined Item Elements
**Endpoint:** `/api/combineditemelements/`
- **Methods:**
  - `GET`: Retrieve a list of all combined item elements.
  - `POST`: Create a new combined item element.
- **Permissions:** Authenticated users only.

**Endpoint:** `/api/combineditemelements/{id}/`
- **Methods:**
  - `GET`: Retrieve a specific combined item element by ID.
  - `PUT/PATCH`: Update a specific combined item element by ID.
  - `DELETE`: Delete a specific combined item element by ID.
- **Permissions:** Authenticated users only.

### Item Nutrients
**Endpoint:** `/api/itemnutrients/`
- **Methods:**
  - `GET`: Retrieve a list of all item nutrients.
  - `POST`: Create a new item nutrient.
- **Permissions:** Authenticated users only.

**Endpoint:** `/api/itemnutrients/{id}/`
- **Methods:**
  - `GET`: Retrieve a specific item nutrient by ID.
  - `PUT/PATCH`: Update a specific item nutrient by ID.
  - `DELETE`: Delete a specific item nutrient by ID.
- **Permissions:** Authenticated users only.

### Item Bioactives
**Endpoint:** `/api/itembioactives/`
- **Methods:**
  - `GET`: Retrieve a list of all item bioactives.
  - `POST`: Create a new item bioactive.
- **Permissions:** Authenticated users only.

**Endpoint:** `/api/itembioactives/{id}/`
- **Methods:**
  - `GET`: Retrieve a specific item bioactive by ID.
  - `PUT/PATCH`: Update a specific item bioactive by ID.
  - `DELETE`: Delete a specific item bioactive by ID.
- **Permissions:** Authenticated users only.

### Item Bioactives
**Endpoint:** `/api/favoriteitems/`
- **Methods:**
  - `GET`: Retrieve a list of all favorite items.
  - `POST`: Create a new fovorite item.
- **Permissions:** Authenticated users only.

**Endpoint:** `/api/favoriteitems/{id}/`
- **Methods:**
  - `GET`: Retrieve a specific fovorite item by ID.
  - `PUT/PATCH`: Update a specific fovorite item by ID.
  - `DELETE`: Delete a specific fovorite item by ID.
- **Permissions:** Authenticated users only.

### Goal Templates
**Endpoint:** `/api/goaltemplates/`
- **Methods:**
  - `GET`: Retrieve a list of all goal templates.
  - `POST`: Create a new goal template.
- **Permissions:** Admin users can modify, read-only for others.

**Endpoint:** `/api/goaltemplates/{id}/`
- **Methods:**
  - `GET`: Retrieve a specific goal template by ID.
  - `PUT/PATCH`: Update a specific goal template by ID.
  - `DELETE`: Delete a specific goal template by ID.
- **Permissions:** Admin users can modify, read-only for others.

### Goal Template Nutrients
**Endpoint:** `/api/goaltemplatenutrients/`
- **Methods:**
  - `GET`: Retrieve a list of all goal template nutrients.
  - `POST`: Create a new goal template nutrient.
- **Permissions:** Admin users can modify, read-only for others.

**Endpoint:** `/api/goaltemplatenutrients/{id}/`
- **Methods:**
  - `GET`: Retrieve a specific goal template nutrient by ID.
  - `PUT/PATCH`: Update a specific goal template nutrient by ID.
  - `DELETE`: Delete a specific goal template nutrient by ID.
- **Permissions:** Admin users can modify, read-only for others.

### User Goals
**Endpoint:** `/api/usergoals/`
- **Methods:**
  - `GET`: Retrieve a list of all user goals.
  - `POST`: Create a new user goal.
- **Permissions:** Authenticated users only.

**Endpoint:** `/api/usergoals/{id}/`
- **Methods:**
  - `GET`: Retrieve a specific user goal by ID.
  - `PUT/PATCH`: Update a specific user goal by ID.
  - `DELETE`: Delete a specific user goal by ID.
- **Permissions:** Authenticated users only.

### User Goal Nutrients
**Endpoint:** `/api/usergoalnutrients/`
- **Methods:**
  - `GET`: Retrieve a list of all user goal nutrients.
  - `POST`: Create a new user goal nutrient.
- **Permissions:** Authenticated users only.

**Endpoint:** `/api/usergoalnutrients/{id}/`
- **Methods:**
  - `GET`: Retrieve a specific user goal nutrient by ID.
  - `PUT/PATCH`: Update a specific user goal nutrient by ID.
  - `DELETE`: Delete a specific user goal nutrient by ID.
- **Permissions:** Authenticated users only.
