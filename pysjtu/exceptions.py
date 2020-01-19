class LoadWarning(UserWarning):
    """ Missing fields in the loaded dict, which may cause a SessionException later. """
    pass


class DumpWarning(UserWarning):
    """ Missing fields in the dumped dict, which may cause a SessionException later. """
    pass


class GPACalculationException(Exception):
    """ A failure has been reported by the remote server when calculating GPA. """
    pass


class SessionException(Exception):
    """ The session is expired or invalid, and we can't renew it automatically. """
    pass


class LoginException(Exception):
    """ An error occurred when logging into the website """
    pass


class ServiceUnavailable(Exception):
    """ The website is down or under maintenance. """
    pass
