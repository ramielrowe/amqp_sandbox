import random

from kombu.common import maybe_declare
from kombu.pools import producers

from queues import task_exchange

priority_to_routing_key = {'info': 'notifications.info',
                           'warn': 'notifications.warn',
                           'error': 'notifications.error'}


def send_as_task(connection, fun, args=(), kwargs={}, priority='info'):
    payload = {'fun': fun, 'args': args, 'kwargs': kwargs}
    routing_key = priority_to_routing_key[priority]

    with producers[connection].acquire(block=True) as producer:
        maybe_declare(task_exchange, producer.channel)
        producer.publish(payload,
                         serializer='pickle',
                         compression='bzip2',
                         exchange=task_exchange,
                         routing_key=routing_key)


if __name__ == '__main__':
    from kombu import Connection
    from tasks import hello_task

    priority = random.choice(priority_to_routing_key.keys())
    #priority = 'info'

    print "Sending on", priority
    connection = Connection('amqp://guest:password@localhost:5672//')
    send_as_task(connection, fun=hello_task, args=('Kombu', ), kwargs={},
                 priority=priority)
