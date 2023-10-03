# Nutrition API Documentation

## Authentication

Authentication is required for most endpoints. The API uses token-based authentication. To obtain an authentication token, send a POST request to the following endpoint:

- **Endpoint:** `/api/api-token-auth/`

**Request:**
```
POST /api/api-token-auth/
Content-Type: application/json
{
    "username": "user_username",
    "password": "user_password"
}
```

**Response:**
```
{
    "token": "user_token"
}
```

Include the obtained token in the `Authorization` header of subsequent requests: `Authorization: Token your_token_here`

## User Management

### Create a User (Sign Up)
- **Endpoint:** `/api/user-create/`
- **Method:** POST

**Request:**
```
POST /api/user-create/
Content-Type: application/json
{
    "is_superuser": false,
    "username": "new_user",
    "password": "new_password",
    "first_name": "John",
    "last_name": "Doe",
    "email": "user@example.com",
    "is_staff": false,
    "age": 30, // in years
    "weight": 180, // in pounds
    "height": 64, // in inches
    "sex": "Male", // "Male" and "Female" (case sensitive) are the only valid values
    "is_pregnant": false
    "is_lactating": false
    
}
```
Only the `username` and `password` fields are required in the request. All other fields are optional.

**Response:**
```
{
    "id": 3,
    "last_login": null,
    "is_superuser": false,
    "username": "new_user",
    "first_name": "John",
    "last_name": "Doe",
    "email": "user@example.com",
    "is_staff": false,
    "is_active": true,
    "date_joined": "2023-09-21T18:37:29.183846-05:00",
    "age": 30,
    "weight": 180,
    "height": 64,
    "sex": "Male",
    "is_pregnant": false
    "is_lactating": false,
    "groups": [],
    "user_permissions": []
}
```

### Create a User and Authenticate (Sign Up and Log In)

- **Endpoint:** `/api/user-create-and-auth/`
- **Method:** POST

**Request:**
```
POST /api/user-create-and-auth/
Content-Type: application/json
{
    "is_superuser": false,
    "username": "new_user",
    "password": "new_password",
    "first_name": "John",
    "last_name": "Doe",
    "email": "user@example.com",
    "is_staff": false,
    "age": 30,
    "weight": 180,
    "height": 64,
    "sex": "Male", // "Male" and "Female" (case sensitive) are the only valid values
    "is_pregnant": false
    "is_lactating": false
}
```
Only the `username` and `password` fields are required in the request. All other fields are optional.

**Response:**
```
{
    "user": {
        "id": 1,
        "last_login": null,
        "is_superuser": false,
        "username": "new_user2",
        "first_name": "John",
        "last_name": "Doe",
        "email": "user@example.com",
        "is_staff": false,
        "is_active": true,
        "date_joined": "2023-09-21T19:03:26.761719-05:00",
        "age": 30,
        "weight": 180,
        "height": 64,
        "sex": "Male",
        "is_pregnant": false
        "is_lactating": false,
        "groups": [],
        "user_permissions": []
    },
    "token": "user_token"
}
```

### Retrieve and Update User Profile

- **Endpoint:** `/api/user-update/`
- **Method:** GET (retrieve), PUT or PATCH (update)

**Request (Retrieve):**
```
GET /api/user-update/
Content-Type: application/json
Authorization: Token user_token
```

**Response (Retrieve):**
```
{
    "username": "new_user",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "age": null,
    "weight": null,
    "height": null,
    "sex": null,
    "is_pregnant": false
    "is_lactating": false
}
```

**Request (Full or Partial Update):**
```
PUT /api/user-update/
Content-Type: application/json
Authorization: Token user_token
{
    "username": "new_username",
    "email": "new_email@example.com",
    "first_name": "NewFirstName",
    "last_name": "NewLastName"
    "age": 30,
    "weight": 180,
    "height": 64,
    "sex": "Male", // "Male" and "Female" (case sensitive) are the only valid values
    "is_pregnant": false
    "is_lactating": false,
}
```
All fields are optional in a PUT or PATCH request. If all are omitted, the request will behave similarly to a GET request.

**Response (Full or Partial Update):**
```
{
    "username": "new_username",
    "email": "new_email@example.com",
    "first_name": "NewFirstName",
    "last_name": "NewLastName"
    "age": 30,
    "weight": 180,
    "height": 64,
    "sex": "Male",
    "is_pregnant": false
    "is_lactating": false,
}
```

### Change Password

- **Endpoint:** `/api/change-password/`
- **Method:** POST

**Request:**
```
POST /api/change-password/
Content-Type: application/json
Authorization: Token user_token
{
    "old_password": "old_password",
    "new_password": "new_password"
}
```

**Response:**
```
{
    "message": "Password changed successfully."
}
```

## User Goal Management

### Generate User Goal

This endpoint generates a user-specific nutrition goal based on user attributes and returns the goal's details, including calorie and nutrient targets. Calorie target is calculated based on user age, weight, height, sex, whether pregnant or lactating, activity level, and diet goal. The macronutrients Carbohydrate, Fat, and Protein are calculated by dividing the calculated calorie target among them.

- **Endpoint:** `/api/user-goal-generate/`
- **Method:** POST

**Request:**
```
POST /api/user-goal-generate/
Content-Type: application/json
Authorization: Token user_token
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

- **Endpoint:** `/api/user-goal-update/{goal_id}/`
- **Method:** GET (retrieve), PUT or PATCH (update)

**Request (Update):**
```
PUT /api/user-goal-detail/{goal_id}/
Content-Type: application/json
Authorization: Token user_token
{
    "name": "New Goal Name",
    "calories": 2000, // Updating calories will update target values for Carbohydrate, Fat, and Protein
    "isActive": true,
    // To update individual goal nutrients, use the endpoint /api/usergoalnutrients/{id}/
}
```
Note for request:
 - The `user` and `template` fields cannot be updated.
 - The `nutrients` field is read-only. To update individual goal nutrients, use the endpoint `/api/usergoalnutrients/{id}/`.
 - To ensure one and only one goal is active per user, the `isActive` field can only be set to `true`, and doing so will deactivate all other goals for the currently authenticated user. To deactivate any given goal, set `isActive` to `true` for any other goal for the user.
 

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


## Summary Statistics

### Goal Nutrient Status

This endpoint provides information about the nutrient status based on the user's active goal. It calculates the total consumption for each nutrient in the active goal based on items consumed by the user on the current date.

- **Endpoint:** `/api/goal-nutrient-status/`
- **Method:** GET

**Request:**
```
GET /api/goal-nutrient-status/
Content-Type: application/json
Authorization: Token user_token
```

**Response:**
```
[
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


## "Regular" View Set Endpoints

These endpoints based on Django REST Framework's ModelViewSet and provide the basic CRUD functionality for each model. These endpoints provide access to all model fields. Details on available fields can be found on the browsable API. If running a local server using the command `python models.py runserver`, you can access the browsable API at http://localhost:8000/api/. You must be logged in to access the browsable API and must be logged in as a superuser for POST, PUT, PATCH, or DELETE operations on certain endpoints.


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
