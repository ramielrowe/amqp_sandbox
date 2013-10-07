from oslo.config import cfg

import logging
from worker.openstack.common import log
from worker.openstack.common.notifier import api

import worker.openstack.common.notifier.rpc_notifier

LOG = log.getLogger(__name__)

publisher = api.publisher_id("worker_client")
payload = {'foo': 1, 'blah': 'zoo'}

# python client.py -d -v --config-file myworker.conf
conf = cfg.CONF()
cfg.set_defaults(log.log_opts,
                 default_log_levels=['amqplib=DEBUG',
                                     'eventlet.wsgi.server=DEBUG'
                                     ])

log.setup('client')

api.notify(None, publisher, "my_event.zap", api.INFO, payload)


