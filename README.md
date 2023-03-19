# Foodgram-react-app
![main](https://github.com/rosh-penin/foodgram-project-react/actions/workflows/foodgram-workflow.yml/badge.svg)
#### Web application for recipes. Realised with React-DRF.

#### Settings
Github workflow file lies in project root folder. You may install project with it.
You need to specify next settings in your github secrets or .env file if you building it manually:  
```sh
DB_ENGINE # If you don't specify engine sqlite3 will be used and rest of the database related settings ignored.
DB_HOST # Default - db. Container name in docker-compose.yaml
DB_NAME # Name of your database
DB_PORT # Database port
POSTGRES_USER # Database user
POSTGRES_PASSWORD # Database password
DJANGO_KEY # Secret key for Django settings.py  

# Next settings only for workflow build
DOCKER_USERNAME # Login to dockerhub
DOCKER_PASSWORD # Password to dockerhub 
HOST # Your server. Either hostname or ip
USER # Username of your server user
SSH_KEY # Also for your server
```
For manual install run:
```sh
sudo docker-compose up -d
```
In folder with docker-compose.yaml.
This will run docker-compose and creates containers.  

### Author: Rosh_penin
### About: Pet project. Web service for recipes with React frontend and Django REST Framework backend realisation.
#### Temporary testing server with deployed project - http://84.201.163.181/