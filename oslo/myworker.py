# -*- encoding: utf-8 -*-
import eventlet
import logging
import socket
import sys


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



class MyWorkerService(service.Service):

    def start(self):
        super(MyWorkerService, self).start()
        # Add a dummy thread to have wait() working
        self.tg.add_timer(604800, lambda: None)

    def initialize_service_hook(self, service):
        LOG.debug('initialize_service_hooks')

        ack_on_error = True

        exchange = cfg.CONF.control_exchange
        queue_name = "notifications.info"
        topic = "notifications.*"
        try:
            self.conn.join_consumer_pool(
                callback=self.process_notification,
                pool_name=queue_name,
                topic=topic,
                exchange_name=exchange,
                ack_on_error=ack_on_error)
        except Exception:
            LOG.exception('Could not join consumer pool %s/%s' %
                          (topic, exchange))

    def process_notification(self, notification):
        LOG.debug('Got notification %r', notification)


def setup_service(argv=None):
    eventlet.monkey_patch()

    # We can leave this as "openstack" default for simple stuff.
    rpc.set_defaults(control_exchange='worker')
    cfg.set_defaults(log.log_opts,
                     default_log_levels=['amqplib=DEBUG',
                                         'eventlet.wsgi.server=DEBUG'
                                         ])
    if argv is None:
        argv = sys.argv
    cfg.CONF(argv[1:], project='worker')
    log.setup('worker')


setup_service()
os_service.launch(MyWorkerService(cfg.CONF.host,
                                  'worker')).wait()
