from oslo.config import cfg

from worker.openstack.common import log
from worker.openstack.common.notifier import api

LOG = log.getLogger(__name__)

publisher = api.publisher_id("worker_client")

payload = {'foo': 1, 'blah': 'zoo'}

# python client.py --config-file myworker.conf
cfg.CONF()
api.notify(None, publisher, "my_event.zap", api.INFO, payload)


