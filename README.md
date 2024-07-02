[![Data engineering assignment test](https://github.com/vkarapatsias/data-eng-project/actions/workflows/main.yml/badge.svg)](https://github.com/vkarapatsias/data-eng-project/actions/workflows/main.yml)

# Data engineering assignment
## Description
`<Some description goes here>`
### Purpose
### Structure
## How to execute
### Setup
On a terminal execute `make install`.
### Execute
On a terminal execute `make run` or `make`.

`docker build -t etl_service .`
`docker run -p 5000:5000 -e SCHIPHOL_API_APP_ID=<your_app_id> -e SCHIPHOL_API_APP_KEY=<your_app_key> -e DB_URI=<your_db_uri> etl_service`

`docker run -e SCHIPHOL_API_APP_ID=your_app_id -e SCHIPHOL_API_APP_KEY=your_app_key -e DB_IP_ADDRESS=ip_address -e DB_USER=db_user DB_PASSWORD=db_password your-app-name`