#!/usr/bin/env python

# Script que percorre todas as apps e groups de um json (de Grupo) removendo:
# app.version
# app.fetch
# group.version

import json
import sys

from marathon.models.group import MarathonGroup
from marathon.util import MarathonJsonEncoder

from hollowman.marathon.group import AsgardAppGroup

data = open(sys.argv[1]).read()
_g = AsgardAppGroup(MarathonGroup.from_json(json.loads(data)))

for group in _g.iterate_groups():
    del group.version
    for app in group.apps:
        del app.version
        del app.fetch
        del app.ports

data_output = json.dumps(_g._marathon_group, cls=MarathonJsonEncoder)
print(data_output)
