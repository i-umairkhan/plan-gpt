#!/bin/bash

# Variables
MYSQL_CONTAINER_NAME="mysql_dbplan-gpt-db"
MYSQL_ROOT_PASSWORD="plan-gpt-db"
MYSQL_DATABASE="mydb"
SCHEMA_NAME="plangptdb"

# # Create and start MySQL Docker container
# docker run -d --name $MYSQL_CONTAINER_NAME -e MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD -p 3306:3306 mysql:latest

# # Wait for MySQL to start
# echo "Waiting for MySQL to start..."
# sleep 10

# Create database
# echo "Creating database $MYSQL_DATABASE..."
docker exec -i $MYSQL_CONTAINER_NAME mysql -uroot -p$MYSQL_ROOT_PASSWORD -e "CREATE DATABASE IF NOT EXISTS $MYSQL_DATABASE;"

# Create schema
echo "Creating schema $SCHEMA_NAME in database $MYSQL_DATABASE..."
docker exec -i $MYSQL_CONTAINER_NAME mysql -uroot -p$MYSQL_ROOT_PASSWORD $MYSQL_DATABASE -e "CREATE SCHEMA IF NOT EXISTS $SCHEMA_NAME;"

npx prisma generate
npx prisma db push


echo "Setup complete."
