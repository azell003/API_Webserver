## Setup

Build Docker image

    docker build -t latest --target production .

Run Docker image

    docker run -p 5000:5000 latest

## Getting Started with the API

Different ways to get started with this stock market simulation API

## User routes 

### Create a user

	curl -v -L -X POST localhost:5000/user/user1

### Retrieve a user

	curl -v -L -X GET localhost:5000/user/user1

### Retrieve all users

	curl -v -L -X GET localhost:5000/user/all

### Delete a user

	curl -v -L -X DELETE localhost:5000/user/user1

## Portfolio routes

### Get all holdings in a portfolio

	curl -v -L -X GET localhost:5000/portfolio/user2/view?date=2017-04-01

### Buying a stock 

	curl -v -L -X POST localhost:5000/portfolio/user2/buy -d "ticker=aapl&date=2017-01-03&qty=10"

### Selling a stock 

	curl -v -L -X POST localhost:5000/portfolio/user2/sell -d "ticker=aapl&date=2017-01-03&qty=10"

### Evaluate portfolio

	curl -v -L -X GET localhost:5000/portfolio/user2/evaluate?date=2017-04-01

### Replace existing portfolio with a CSV file 

	curl -v -L -X POST --form file='@trades.csv' localhost:5000/portfolio/user2/replace

### Clearing existing holdings

	curl -v -L -X DELETE localhost:5000/portfolio/user1/clear_holdings

### Query stock price information

	curl -v -L -X GET localhost:5000/portfolio/stock/aapl?date=2017-01-03
