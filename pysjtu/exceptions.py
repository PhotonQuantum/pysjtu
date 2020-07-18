class LoadWarning(UserWarning):
    """ Missing fields in the loaded dict, which may cause a SessionException later. """


class DumpWarning(UserWarning):
    """ Missing fields in the dumped dict, which may cause a SessionException later. """


class GPACalculationException(Exception):
    """ A failure has been reported by the remote server when calculating GPA. """


class SelectionClassFetchException(Exception):
    """ Unable to fetch selection class information. """


class SessionException(Exception):
    """ The session is expired or invalid, and we can't renew it automatically. """


class LoginException(Exception):
    """ An error occurred when logging into the website """


class ServiceUnavailable(Exception):
    """ The website is down or under maintenance. """
