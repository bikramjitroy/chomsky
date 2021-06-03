# VINSIGHT

> This is a Bot Conversation analytics!

## Table of contents

- [General info](#general-info)
- [Setup for first time run](#setup-for-first-time-run)
- [Database and Databse-schema](#database-and-databse-schema)
- [Configuration of postgress-database url](#features)
- [Application Run](#application-run)
- [Test Run](#test-run)

## General info

This will help us to get complete analysis of bot conversation

## Setup for first time run

#### If the bot is being set up for first time, follow below steps for `mkcert` installation :

- `sudo apt install libnss3-tools -y`
- `sudo apt install linuxbrew-wrapper`
- `brew install mkcert`
- `PATH="/home/linuxbrew/.linuxbrew/bin:$PATH"`

- `mkdir certs`

  - (i. If 'certs' directory already exists delete and make the dir again.)
  - (ii. Put the certficates in the 'certs' dir.)

- `mkcert -install`
- `mkcert -cert-file certs/local-cert.pem -key-file certs/local-key.pem "docker.localhost" "*.docker.localhost" "domain.local" "*.domain.local"`

## Database and Databse-schema

## Configuration of postgress-database url

#### Configure below parameters in `.env` file.

- DB_DATABASE=<data-base name>
- DB_HOST=<ip>
- DB_USERNAME=<user_name>
- DB_PASSWORD=<password>
- DB_PORT=<port>
- ORIGIN_URL="https://chomsky.ameyo.net:9005"

## Application Run

#### For first time run only run this command :

- `docker network create proxy`

#### Command to run the application through docker:

- `docker-compose up --build`

#### In browser run below url for runtime experience of your bot

- `https://chomsky.ameyo.net:9005/api/v1/home?botid=<bot_id of your bot>`

## Test Run

- Edit test_varfile for required configuration for testing.
- All the api can be tested in one go, or please comment or uncomment according to the need of testing.

#### Test run command :

- `docker-compose -f docker-compose-test.yml up --build`
