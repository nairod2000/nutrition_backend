# nutrition_backend

## Database Setup

### Installing PostgreSQL

The project relies on PostgreSQL as the database management system. If you haven't installed PostgreSQL, follow these steps to do so:

  1. Visit the PostgreSQL Downloads page: https://www.postgresql.org/download/
  2. Choose the appropriate installer for your operating system.
  3. Follow the installation instructions provided for your platform.
  4. Open your PostgreSQL shell and create a database for this project. (E.g., `CREATE DATABASE nutrition;`)

### Setting up Environment Variables with .env

To manage sensitive information like database credentials and other configuration variables, we use a .env file. This file is not included in version control and should be kept private.

#### Step 1: Install Required Packages

You will need python-decouple and psycopg2. They should install automatically via the requirements.txt file if you are using a virtual environment. Otherwise install manually:

- `pip install python-decouple`
- `pip install psydopg2`

#### Step 2: Create a New .env File

1. Navigate to the root directory of the project.
2. Create a new file named .env.

#### Step 3: Add Environment Variables

Open the .env file you created and add the following lines:

DB_NAME=my_database_name
DB_USER=my_database_user
DB_PASSWORD=my_database_password
DB_HOST=my_database_host
DB_PORT=my_database_port

Replace the placeholders (my_database_name, my_database_user, etc.) with your actual database credentials and configurations.

#### Step 4: Updating Environment Variables

If any of the configuration values change (e.g., database credentials), update them in the .env file. Make sure not to commit this file to version control.

#### Important Note:

- Never share your .env file publicly or commit it to version control. It contains sensitive information.
- Ensure that each team member creates their own .env file with their specific credentials.

### Perform Migrations, Create Admin Account, Run Server

Run the following commands from the project root directory to create and apply migrations to your local PostgreSQL database:
`python manage.py makemigrations` (only required if you have modified a model)
`python manage.py migrate`

Run `python manage.py createsuperuser` to create a superuser account.
Run `python manage.py runserver` to start a local server.
Access the admin interface at http://localhost:8000/admin/