# IntelligentAttendanceSolution
I am building one web app to manage institute attandence and send notification to respected users of app, attendance by face recoginaztion and manaual marking

## Requirements
1. Python 3.8 if you don't have that you can download from [here](https://www.python.org/downloads/release/python-381) or from `dependencies_for_windows` if windows os

## Installation and run locally
1. Clone the repository
```
git clone https://github.com/PritishDighore26/IntelligentAttendanceSolution.git
```

2. Create virtual environment and activate
For windows
```
py -V:3.8 -m venv venv
.\venv\Scripts\activate
```

3. Install CMake and Visual Studio Setup for dlib from `dependencies_for_windows` folder

4. Use Make commands to run any command from the project if you don't have make utility then install from [here](https://stackoverflow.com/questions/32127524/how-to-install-and-use-make-in-windows)
- To install project packages and dependencies run `make install`
- To update and migrate DB changes `make update`
- Only migrate run `make migrate`
- To run server `make runserver`


# Create a django project and add APPS
1. `django-admin startproject IAS .` to create django project
2. `python manage.py startapp <app name>` to create django app

# Commands for migration in Database
1. `python manage.py makemigrations` to make migration files available
2. `python manage.py migrate` to migrate the changes to database

# Commands to create super user (For Development)
1. `python manage.py createsuperuser` to create super user
