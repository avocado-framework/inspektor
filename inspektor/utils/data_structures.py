class Borg:

    """
    Multiple instances of this class will share the same state.

    This is considered a better design pattern in Python than
    more popular patterns, such as the Singleton. Inspired by
    Alex Martelli's article mentioned below:

    :see: http://www.aleax.it/5ep.html
    """

    __shared_state = {}

    def __init__(self):
        self.__dict__ = self.__shared_state
