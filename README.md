Kettle
======

Kettle is an implementation of the Kademlia DHT written in Python using asyncio.


## Status

Work-in-progress.

Not suitable for children under 3.


## Usage

    from kettle import Node, get_event_loop

    # Synchronous.
    node = Node(('127.0.0.1', 8800), loop=get_event_loop())
    node.run_forever()

    # Asynchronous.
    node = Node(('127.0.0.1', 8888), loop=get_event_loop())
    node.listen()

    # Poke another node.
    node.ping(('1.2.3.4', 8080))

    # Store your bytes.
    node.store(('1.2.3.4', 8080), 'Be sure to drink your Round-tine')

