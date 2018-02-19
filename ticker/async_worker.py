import aiohttp
import asyncio
import pika
import json


async def alive():
    while True:
        await asyncio.sleep(30)
        channel.basic_publish(exchange='', routing_key='', body='')


async def send_to_queue(message):
    channel.basic_publish(exchange='bitso', routing_key='bitso-key',
                          body=json.dumps(message), properties=properties)


async def message_handler(book, msg):
    if 'trades' in msg.values():
        if msg['payload']:
            print(book, msg['payload'][0]['r'])
            await send_to_queue({book: msg['payload'][0]['r']})


async def ticker(book):
    session = aiohttp.ClientSession()
    async with session.ws_connect('wss://ws.bitso.com') as ws:
        await ws.send_json({'action': 'subscribe', 'book': book, 'type': 'trades'})
        await ws.receive_json()
        print('Subscribed to:', book)
        async for msg in ws:
            if msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                break
            await message_handler(book, msg.json())

if __name__ == '__main__':
    parameters = pika.ConnectionParameters(host='rabbitmq',
                                           socket_timeout=10,
                                           retry_delay=5,
                                           connection_attempts=3)
    connection = pika.BlockingConnection(parameters=parameters)
    channel = connection.channel()

    channel.exchange_declare(exchange='bitso', exchange_type='fanout')
    channel.queue_declare(queue='bitso-queue', durable=True)
    channel.queue_bind(exchange='bitso', queue='bitso-queue', routing_key='bitso-key')
    properties = pika.BasicProperties(content_type='application/json')

    books = ['btc_mxn', 'eth_mxn', 'xrp_mxn']
    alive_gather = asyncio.gather(alive())
    tickers_gather = asyncio.gather(*[ticker(book) for book in books])
    all_gathers = asyncio.gather(alive_gather, tickers_gather)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(all_gathers)
    loop.close()
