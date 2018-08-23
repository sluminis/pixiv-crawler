class SpiderError(Exception):
    pass

# Sentinel used for shutdown
class ActorExit(SpiderError):
    pass

class NetworkError(SpiderError):
    pass
