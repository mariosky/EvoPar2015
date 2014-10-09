__author__ = 'mariosky'

# http://aws.amazon.com/sdk-for-python/
# Jugando con la libreria de amazon para la gestion de maquinas virtuales EC2

import boto.ec2
import aws_keys

import time
from fabric.tasks import execute
from fabric.api import *


print boto.ec2.regions()

conn = boto.ec2.connect_to_region("us-east-1",
                                  aws_access_key_id=aws_keys.aws_access_key_id,
                                  aws_secret_access_key=aws_keys.aws_secret_access_key)


reservations = conn.run_instances(
        'ami-884bf7e0',
        key_name='evospace',
        instance_type='m3.medium',
        security_groups=['launch-wizard-1'])

time.sleep(10)

for instance in reservations.instances:
    while instance.state != "running":
        time.sleep(5)
        instance.update()
        print instance.state
    print instance.state
    print "running"


print reservations.instances[0].id
print reservations.instances[0].ip_address


print "waiting..."
time.sleep(40)


def execute_task():
    sudo('python evospace/cherry_server.py')

env.hosts = [reservations.instances[0].public_dns_name]
env.user = 'ubuntu'
env.key_filename = 'evospace.pem'

execute(execute_task)
conn.terminate_instances(instance_ids=[reservations.instances[0].id])

