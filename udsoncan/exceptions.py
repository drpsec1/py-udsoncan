from __future__ import absolute_import
import inspect
def service_name(service):
    if inspect.isclass(service):
        return unicode(service.__name__)
    else:
        return unicode(service.__class__.__name__)

class TimeoutException(Exception):
    u"""
    Simple extension of ``Exception`` with no additional property. Raised when a timeout in the communication happens.
    """
    def __init__(self, *args, **kwargs):
        super(TimeoutException, self).__init__(*args, **kwargs)

class NegativeResponseException(Exception):
    u"""
    Raised when the server returns a negative response (response code starting by 0x7F).
    The response that triggered the exception is available in ``e.response``

    :param response: The response that triggered the exception
    :type response: :ref:`Response<Response>`
    """
    def __init__(self, response, *args, **kwargs):
        self.response = response
        msg = self.make_msg(response)
        if len(args) > 0 :
            msg += u" "+unicode(args[0])
            args = tuple(list(args)[1:])
        super(NegativeResponseException, self).__init__(msg, *args, **kwargs)

    def make_msg(self, response):
        servicename = response.service.get_name()+u" " if response.service is not None else u""
        return u"%sservice execution returned a negative response %s (0x%x)" % (servicename, response.code_name, response.code)

class InvalidResponseException(Exception):
    u"""
    Raised when a service fails to decode a server response data. A bad message length or a value that is out of range may both be valid causes.
    The response that triggered the exception is available in ``e.response``

    :param response: The response that triggered the exception
    :type response: :ref:`Response<Response>`
    """

    def __init__(self, response, *args, **kwargs):
        self.response = response
        msg = self.make_msg(response)
        if len(args) > 0 :
            msg += u" "+unicode(args[0])
            args = tuple(list(args)[1:])
        super(InvalidResponseException, self).__init__(msg, *args, **kwargs)

    def make_msg(self, response):
        servicename = response.service.get_name()+u" " if response.service is not None else u""
        reason = u"" if response.valid else u" Reason : %s" % (response.invalid_reason)
        return u"%sservice execution returned an invalid response.%s" % (servicename,reason)

class UnexpectedResponseException(Exception):
    u"""
    Raised when the client receives a valid response but considers the one received to not be the expected response.
    The response that triggered the exception is available in ``e.response``

    :param response: The response that triggered the exception
    :type response: :ref:`Response<Response>`

    :param details: Additional details about the error
    :type details: string
    """
    def __init__(self, response, details=u"<No details given>", *args, **kwargs):
        self.response = response
        msg = self.make_msg(response, details)
        if len(args) > 0 :
            msg += u" "+unicode(args[0])
            args = tuple(list(args)[1:])
        super(UnexpectedResponseException, self).__init__(msg, *args, **kwargs)

    def make_msg(self, response, details):
        servicename = response.service.get_name()+u" " if response.service is not None else u""
        return u"%sservice execution returned a valid response but unexpected. Details : %s " % (servicename, details)

class ConfigError(Exception):
    u"""
    Raised when a bad configuration element is encountered.

    :param key: The configuration key that failed to resolve properly
    :type key: object

    """
    def __init__(self, key, msg=u"<No details given>", *args, **kwargs):
        self.key=key
        super(ConfigError, self).__init__(msg, *args, **kwargs)
