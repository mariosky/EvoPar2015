__author__ = 'mariosky'

from fabric.api import *
import boto.ec2
import aws_keys


import boto.ec2
import aws_keys

import time
from fabric.tasks import execute
from fabric.api import *

EC2_REGION = "us-east-1"

print "Connecting to Region:",  EC2_REGION

conn = boto.ec2.connect_to_region("us-east-1",
                                  aws_access_key_id=aws_keys.aws_access_key_id,
                                  aws_secret_access_key=aws_keys.aws_secret_access_key)


reservations = conn.run_instances(
        "ami-84ef55ec",min_count=2, max_count=2,
        key_name='evospace',
        instance_type='m3.medium',
        security_groups=['launch-wizard-1'])

time.sleep(10)

#
# Wait Method
#
for instance in reservations.instances:
    while instance.state != "running":
        time.sleep(5)
        instance.update()
        print instance.state
    print instance.state
    print "running"



print "waiting..."
time.sleep(40)

def execute_task():
    put(local_path='one_max.py', remote_path="EvoPar2015/code/one_max.py" )
    with cd("EvoPar2015/code"):
        sudo("celery -A one_max worker --detach --loglevel=info")


env.hosts = [instance.public_dns_name for instance in reservations.instances]
env.user = 'ubuntu'
env.key_filename = 'evospace.pem'

execute(execute_task)

#celery -A one_max worker --detach --loglevel=info
