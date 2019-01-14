import sys
sys.path.insert(0, '/opt/prophetstor/alameter/api')


from alameter_api import app as application

import os

with open('/opt/prophetstor/alameter/alameter.env') as f:
    for raw in f:
        line = raw.split()[0]
        pos = line.find("=")
        os.environ[line[:pos]] = line[pos+1:]

application.debug = True
