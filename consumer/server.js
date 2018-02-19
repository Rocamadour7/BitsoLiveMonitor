var amqp = require('amqplib/callback_api');
var app = require('express')();
var server = require('http').Server(app);
var io = require('socket.io')(server);

server.listen(8080);

var emitter = io.of('/');

function consumer(conn) {
  var ok = conn.createChannel(on_open);
  function on_open(err, ch) {
    if (err != null) {
      startRabbitMQ('Error creating channel with RabbitMQ!... Reconnecting');
    }
    ch.assertQueue('bitso-queue');
    ch.consume('bitso-queue', function(msg) {
      if (msg !== null) {
        json_msg = JSON.parse(msg.content);
        emitter.emit('new-trade', json_msg);
        console.log(json_msg);
        ch.ack(msg);
      }
    });
  }
}

function connectRabbitMQ() {
  amqp.connect('amqp://rabbitmq', function(err, conn) {
      if (err != null) {
        startRabbitMQ('Error connecting with RabbitMQ!... Reconnecting');
      } else {
        consumer(conn);
      }
    });
}

function startRabbitMQ(err) {
  if (err != null) console.log(err);
  setTimeout(connectRabbitMQ, 5000);
}

startRabbitMQ();
