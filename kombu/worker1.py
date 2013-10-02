from kombu.mixins import ConsumerMixin
from kombu.log import get_logger
from kombu.utils import kwdict, reprcall

from queues import task_queues1

logger = get_logger(__name__)


class Worker(ConsumerMixin):

    def __init__(self, connection):
        self.connection = connection

    def get_consumers(self, Consumer, channel):
        print "Returning consumers ..."
        return [Consumer(queues=task_queues1,
                         callbacks=[self.process_task])]

    def process_task(self, body, message):
        fun = body['fun']
        args = body['args']
        kwargs = body['kwargs']
        print('Got task: %s on %s' %
            (reprcall(fun.__name__, args, kwargs),
            message.delivery_info))
        try:
            fun(*args, **kwdict(kwargs))
        except Exception, exc:
            print('task raised exception: %r' % exc)
        message.ack()


if __name__ == '__main__':
    from kombu import Connection
    from kombu.utils.debug import setup_logging
    setup_logging(loglevel='INFO')

    with Connection('amqp://guest:password@localhost:5672//') as conn:
        try:
            conn.connect()
            print "Starting ....", conn.connected
            Worker(conn).run()
        except KeyboardInterrupt:
            print('bye bye')
