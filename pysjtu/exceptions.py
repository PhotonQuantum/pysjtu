class LoadWarning(UserWarning):
    """ Missing fields in the loaded dict, which may cause a SessionException later. """


class DumpWarning(UserWarning):
    """ Missing fields in the dumped dict, which may cause a SessionException later. """


class GPACalculationException(Exception):
    """ A failure has been reported by the remote server when calculating GPA. """


class SelectionNotAvailableException(Exception):
    """ Course selection function is not available at this time. """


class SelectionClassFetchException(Exception):
    """ Unable to fetch selection class information. """


class RegistrationException(Exception):
    """ Base exception for class registration failures. """


class DeregistrationException(Exception):
    """ Base exception for class deregistration failures. """


class FullCapacityException(RegistrationException):
    """ There's no room for this class. """


class TimeConflictException(RegistrationException):
    """ There's a time conflict when registering for this class. """


class SessionException(Exception):
    """ The session is expired or invalid, and we can't renew it automatically. """


class LoginException(Exception):
    """ An error occurred when logging into the website """


class OCRException(Exception):
    """ An error occurred when solving captcha """


class ServiceUnavailable(Exception):
    """ The website is down or under maintenance. """
