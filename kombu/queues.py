from kombu import Exchange, Queue

task_exchange = Exchange('tasks', type='topic')
task_queues = [Queue('queue1', task_exchange,
               routing_key='notifications.info'),]
task_queues1 = [Queue('queue2', task_exchange,
                routing_key='notifications.*'),]
