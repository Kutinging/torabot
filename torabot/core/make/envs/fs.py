import os
from .base import Base


class Env(Base):

    def __init__(self, root):
        super(Env, self).__init__()
        self.root = root

    def read(self, name):
        with open(os.path.join(self.root, name), 'rb') as f:
            return f.read()
