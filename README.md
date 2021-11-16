Boilerplate LTI 1.3 template written in Python using the Flask framework.
==========================================================

# About

This is our starter Flask Template for using LTI 1.3.  This skeleton will launch an LTI 1.3 application from within your LMS and display the email of the logged in user.  

# Installation

## Docker

## Development 

First you will need to clone the repo, and create the environment file from the template.  


```sh
git clone git@github.com:ucfopen/lti-simple.git
cd lti-simple
cp .env.template .env

```

In this simple framework all the variables are preset, but for production you will want to you will want to edit the .env environment variables DEBUG and SECRET_KEY.

We use Docker-Compose to build and run our services.

```sh
docker-compose build
docker-compose up -d
```

After Docker builds and starts the services, you will run the migration commands to create the database.


```sh
docker-compose exec lti flask db upgrade 
```

The database which will hold your LTI1.3 credentials is now created.  It's now time to generate the LTI 1.3 keys for LMS authentication:

```sh
docker-compose run lti python generate_keys.py 
```

Follow these instructions to install the LTI 1.3 Template into your CanvasLMS. 

You will then enter the LMS generated client id into the command above, then install the app into one of your courses and then add the deployment id from the Course Settings page.

The LTI 1.3 Template will now be available at: <http://127.0.0.1:8000/lti13template/>


