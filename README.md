# Bitso Live Monitor
[![Build Status](https://travis-ci.org/Rocamadour7/BitsoLiveMonitor.svg?branch=master)](https://travis-ci.org/Rocamadour7/BitsoLiveMonitor)
[![Coverage Status](https://coveralls.io/repos/github/Rocamadour7/BitsoLiveMonitor/badge.svg?branch=master)](https://coveralls.io/github/Rocamadour7/BitsoLiveMonitor?branch=master)

Project to practice concepts like TDD, CI, containers, message queues.

Using tools like:
* Travis-CI
* Coveralls
* Docker
* RabbitMQ

### Requirements:
* Python 3.6
* Requests
* Python-dotenv
* aiohttp
* NodeJS
* Express
* amqplib
* socket.io
* Docker
* docker-compose

### How to run

1. Clone this repo `git clone https://github.com/Rocamadour7/BitsoLiveMonitor.git`
2. Run docker-compose `docker-compose up`
3. Browse to `localhost:8080` to check the RabbitMQ management tool, to see the ticker and the producer in action.
4. Open `test.html`, then go to the console, to check that it is receiving realtime updates from the server.

*Work in progress*

*Soon to be implemented real-time web interface.*
