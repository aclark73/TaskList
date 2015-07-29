class EventHook(object):

    def __init__(self):
        self.__handlers = []

    def add(self, handler):
        self.__handlers.append(handler)
        return self

    def __iadd__(self, handler):
        self.add(handler)

    def remove(self, handler):
        self.__handlers.remove(handler)
        return self

    def __isub__(self, handler):
        self.remove(handler)

    def fire(self, *args, **keywargs):
        for handler in self.__handlers:
            handler(*args, **keywargs)

    def clearObjectHandlers(self, inObject):
        for theHandler in self.__handlers:
            if theHandler.im_self == inObject:
                self -= theHandler
