import jsonpickle
from .base import Base


class Target(Base):

    unary = True

    def __call__(self, text):
        return jsonpickle.decode(text)