# so we have parity with fabric
from fabric.api import *

from fake.state import paths
from fake.decorators import task
from fake.context_managers import cd
from fake.tasks.helpers import before, after
from fake.operations import test
