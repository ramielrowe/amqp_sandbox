# -*- encoding: utf-8 -*-
import eventlet
import os
import socket
import sys

cwd = os.getcwd()

sys.path.append(os.path.normpath(cwd))

from oslo.config import cfg

from worker.openstack.common import log
from worker.openstack.common import rpc
from worker.openstack.common.rpc import service
from worker.openstack.common import service as os_service

LOG = log.getLogger(__name__)

cfg.CONF.register_opts([
    cfg.StrOpt('host',
               default=socket.gethostname(),
               help='Name of this node.  This can be an opaque identifier.  '
               'It is not necessarily a hostname, FQDN, or IP address. '
               'However, the node name must be valid within '
               'an AMQP key, and if using ZeroMQ, a valid '
               'hostname, FQDN, or IP address'),
])



class CollectorService(service.Service):

    def start(self):
        super(CollectorService, self).start()
        # Add a dummy thread to have wait() working
        self.tg.add_timer(604800, lambda: None)

    def initialize_service_hook(self, service):
        LOG.debug('initialize_service_hooks')

        ack_on_error = False

        exchange = "tasks"
        topic = "queue_a"
        try:
            self.conn.join_consumer_pool(
                callback=self.process_notification,
                pool_name=topic,
                topic=topic,
                exchange_name=exchange,
                ack_on_error=ack_on_error)
        except Exception:
            LOG.exception('Could not join consumer pool %s/%s' %
                          (topic, exchange))

    def process_notification(self, notification):
        """RPC endpoint for notification messages

        When another service sends a notification over the message
        bus, this method receives it. See _setup_subscription().

        """
        LOG.debug('notification %r', notification.get('event_type'))


def prepare_service(argv=None):
    eventlet.monkey_patch()
    rpc.set_defaults(control_exchange='worker')
    cfg.set_defaults(log.log_opts,
                     default_log_levels=['amqplib=DEBUG',
                                         'qpid.messaging=INFO',
                                         'sqlalchemy=WARN',
                                         'keystoneclient=INFO',
                                         'stevedore=INFO',
                                         'eventlet.wsgi.server=DEBUG'
                                         ])
    if argv is None:
        argv = sys.argv
    cfg.CONF(argv[1:], project='worker')
    log.setup('worker')



prepare_service()
os_service.launch(CollectorService(cfg.CONF.host,
                                       'worker')).wait()
