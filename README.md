Boilerplate LTI 1.3 template written in Python using the Flask framework
==========================================================

## About

This is our starter Flask Template for using LTI 1.3.  This skeleton will launch an LTI 1.3 application from within your LMS and display the email of the logged in user.  

We are always looking for feedback and pull requests.

## Docker Development

First you will need to clone the repo, and create the environment file from the template.  

```sh
git clone https://github.com/ucfopen/lti-13-template-flask
cd lti-13-template-flask
cp .env.template .env

```

In this simple framework all the variables are preset, but for production you will want to edit the .env environment variables DEBUG and SECRET_KEY.

We use Docker-Compose to build and run our services.

```sh
docker-compose build
docker-compose up -d
```

After Docker builds and starts the services, you will run the migration commands to create the database.

```sh
docker-compose exec lti flask db upgrade 
```

The database which will hold your LTI1.3 credentials has now been created.  It's now time to generate the LTI 1.3 keys for LMS authentication:

```sh
docker-compose run lti python generate_keys.py 
```

This script will output directions to follow to generate the Client ID and Deployment ID.  You can find further documentation here: <https://github.com/dmitry-viskov/pylti1.3/wiki/Configure-Canvas-as-LTI-1.3-Platform>

The LTI 1.3 Template will now be running at: <http://127.0.0.1:8000/lti13template/> and available via the course navigation from the account or course you installed the tool into.

Special Thanks
==========================================================

[Dmitry Viskov](https://github.com/dmitry-viskov/) for the [pylti1p3](https://github.com/dmitry-viskov/pylti1.3/) python library.

[Instructure](https://github.com/instructure/) for their LMS: [Canvas](https://github.com/instructure/canvas-lms)

[IMS Global](https://imsglobal.org) for defining the LTI standards.
