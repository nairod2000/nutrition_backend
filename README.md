## Database Setup

### Installing PostgreSQL

To install PostreSQL, which we are using four the project database, visit https://www.postgresql.org/download/ and find the installer for your operating system. Once you have it installed, open the PostgreeSQL shell and create a database on your computer using the command `CREATE DATABASE nutrition;`.

### Environment Variables

Instead of hardcoding our personal database credentials into the settings.py file in the project backend, use a .env file to hold them. The settings.py file will then reference this file. This .env will be ignored by version control and will thus keep your info private.

If you are using a virtual environment (which you should be), the two following packages should install automatically since they are included in the requirements.txt file. Otherwise install them manually:

- `pip install python-decouple`
- `pip install psydopg2`

Create a new file in the nutrition_backend folder named ".env" and add the following lines to it. Replace myDatabaseName, myUsername, etc. with your own database and login info.
```
DB_NAME=myDatabaseName
DB_USER=myUsername
DB_PASSWORD=myPassword
DB_HOST=databaseHost
DB_PORT=databasePort
```

### Build the Database, Create a Superuser Account, and Run the Server

From the root project folder (nutrition_backend), run these commands:
`python manage.py makemigrations` (You only need to run this if you have changed a model in the models.py file)
`python manage.py migrate` (Builds the database)
`python manage.py createsuperuser`
`python manage.py runserver 0.0.0.0:8000`
You can open the nutriton backend admin page in your browser: http://localhost:8000/admin/.