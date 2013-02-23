"""
There is an exception class for each of the error codes defined here:

http://www.last.fm/api/errorcodes

"""
from collections import defaultdict


class LastfmError(Exception):
    """Base exception class."""
    code = None

    def __init__(self, message, code=code):
        doc = ' '.join(type(self).__doc__.split())
        self.message = 'Last.fm API response error code %s (%s): %s' % (
            self.code, doc, message)
        if code:
            assert not self.code or self.code == code
            self.code = code

    def __str__(self):
        return self.message


EXCEPTIONS_BY_CODE = defaultdict(LastfmError)


### Base categories.
class AuthError(object): pass
class ServerError(object): pass
class ClientError(object): pass
class TemporaryError(object): pass
class StationError(object): pass


### Exceptions for each error code.
class UnknownError(LastfmError):
    """This error code isn't known."""

class InvalidServiceError(LastfmError, ClientError):
    """Invalid service -This service does not exist"""
    code = 2

class InvalidMethodError(LastfmError, ClientError):
    """Invalid Method - No method with that name in this package"""
    code = 3

class AuthenticationError(LastfmError, AuthError):
    """Authentication Failed - You do not have permissions to access
    the service"""
    code = 4

class InvalidFormatError(LastfmError, ClientError):
    """Invalid format - This service doesn't exist in that format"""
    code = 5

class InvalidParametersError(LastfmError, ClientError):
    """Invalid parameters - Your request is missing a required parameter"""
    code = 6

class InvalidResourceError(LastfmError, ClientError):
    """Invalid resource specified"""
    code = 7

class OperationFailedError(LastfmError, ServerError, TemporaryError):
    """Operation failed - Most likely the backend service failed.
    Please try again."""
    code = 8

class InvalidSessionKeyError(LastfmError):
    """Invalid session key - Please re-authenticate"""
    code = 9

class InvalidAPIKeyError(LastfmError, AuthError, ClientError):
    """Invalid API key - You must be granted a valid key by last.fm"""
    code = 10

class ServiceOfflineError(LastfmError, TemporaryError, ServerError):
    """Service Offline - This service is temporarily offline.
    Try again later."""
    code = 11

class SubscribersOnlyError(LastfmError):
    """Subscribers Only - This station is only available to paid
    last.fm subscribers"""
    code = 12

class InvalidSignatureError(LastfmError, AuthError, ClientError):
    """Invalid method signature supplied"""
    code = 13

class UnauthorizedTokenError(LastfmError, AuthError, ClientError):
    """Unauthorized Token - This token has not been authorized"""
    code = 14

class StreamingUnavailableError(LastfmError, ClientError):
    """This item is not available for streaming."""
    code = 15

class ServiceTemporarilyUnavailableError(LastfmError,
                                         ServerError,
                                         TemporaryError):
    """The service is temporarily unavailable, please try again."""
    code = 16

class LoginRequiredError(LastfmError, AuthError, ClientError):
    """Login: User requires to be logged in"""
    code = 17

class TrialExpiredError(LastfmError):
    """Trial Expired - This user has no free radio plays left.
    Subscription required."""
    code = 18

class NotEnoughContentError(LastfmError, StationError):
    """Not Enough Content - There is not enough content to play
    this station"""
    code = 20

class NotEnoughMembersError(LastfmError, StationError):
    """Not Enough Members - This group does not have enough
    members for radio"""
    code = 21

class NotEnoughFansError(LastfmError, StationError):
    """Not Enough Fans - This artist does not have enough
    fans for for radio"""
    code = 22

class NotEnoughNeighboursError(LastfmError, StationError):
    """Not Enough Neighbours - There are not enough neighbours for radio"""
    code = 23

class NoPeakRadioError(LastfmError, StationError, TemporaryError):
    """No Peak Radio - This user is not allowed to
    listen to radio during peak usage"""
    code = 24

class RadioNotFoundError(LastfmError, StationError, ClientError):
    """Radio Not Found - Radio station not found"""
    code = 25

class APIKeySuspendedError(LastfmError, AuthError, ClientError):
    """API Key Suspended - This application is not allowed
    to make requests to the web services"""
    code = 26

class DeprecatedError(LastfmError, ClientError):
    """Deprecated - This type of request is no longer supported"""
    code = 27

class RateLimitExceededError(LastfmError, TemporaryError, ClientError):
    """Rate Limit Exceeded - Your IP has made too many requests
    in a short period, exceeding our API guidelines"""
    code = 29


for cls in LastfmError.__subclasses__():
    EXCEPTIONS_BY_CODE[cls.code] = cls
