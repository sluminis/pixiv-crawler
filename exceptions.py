# Sentinel used for shutdown
class ActorExit(Exception):
    pass

class SpiderError(Exception):
    pass

class NetworkError(SpiderError):
    pass
