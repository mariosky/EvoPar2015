__author__ = 'mariosky'

# http://aws.amazon.com/sdk-for-python/


import boto.ec2
import aws_keys

import time

print boto.ec2.regions()

conn = boto.ec2.connect_to_region("us-east-1",
                                  aws_access_key_id=aws_keys.aws_access_key_id,
                                  aws_secret_access_key=aws_keys.aws_secret_access_key)


reservations = conn.run_instances(
        'ami-e84d8480',
        key_name='evospace',
        instance_type='m3.medium',
        security_groups=['launch-wizard-1'])

time.sleep(10)


for instance in reservations.instances:
    while instance.state != "running":
        time.sleep(5)
        print instance.state
    print instance.state
    print "running"