from oslo.config import cfg

import logging
from worker.openstack.common import log
from worker.openstack.common.notifier import api

import worker.openstack.common.notifier.rpc_notifier

LOG = log.getLogger(__name__)
logging.basicConfig(filename='example.log',level=logging.DEBUG)

publisher = api.publisher_id("worker_client")

payload = {'foo': 1, 'blah': 'zoo'}

# python client.py --config-file myworker.conf
conf = cfg.CONF
conf()
print "Log opts"
conf.log_opt_values(LOG, logging.INFO)

print "Config", cfg.CONF.notification_topics
api.notify(None, publisher, "my_event.zap", api.INFO, payload)


