from django.conf import settings
from Neo4j.models import *
import aiml
import os

def init_kernel():
    kernel = aiml.Kernel()
    kernel.bootstrap(learnFiles=os.path.abspath("Neo4j/Data/*.aiml"))
    return kernel