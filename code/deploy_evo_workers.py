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
        "ami-40149128",min_count=4, max_count=4,
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
    put(local_path='ppeaks_worker.py', remote_path="EvoPar2015/code/ppeaks_worker.py" )
    put(local_path='ppeaks.py', remote_path="EvoPar2015/code/ppeaks.py" )
    put(local_path='celeryd', remote_path="/etc/default/celeryd",  use_sudo=True, mode=0640)
    sudo("chown root /etc/default/celeryd")
    sudo("service celeryd start")


env.hosts = [instance.public_dns_name for instance in reservations.instances]
env.user = 'ubuntu'
env.key_filename = 'evospace.pem'

execute(execute_task)

#celeryd -A one_max worker --detach --loglevel=info
