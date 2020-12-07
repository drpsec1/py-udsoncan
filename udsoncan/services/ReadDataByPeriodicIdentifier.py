from __future__ import absolute_import
from . import *
from udsoncan.Response import Response
from udsoncan.exceptions import *

class ReadDataByPeriodicIdentifier(BaseService):
    _sid = 0x2A

    supported_negative_response = [	 Response.Code.IncorrectMessageLengthOrInvalidFormat,
                                                    Response.Code.ConditionsNotCorrect,
                                                    Response.Code.RequestOutOfRange,
                                                    Response.Code.SecurityAccessDenied
                                                    ]

    @classmethod
    def make_request(cls):
        raise NotImplementedError(u'Service is not implemented')

    @classmethod
    def interpret_response(cls, response):
        raise NotImplementedError(u'Service is not implemented')

    class ResponseData(BaseResponseData):	
        def __init__(self):
            super(ReadDataByPeriodicIdentifier.ResponseData, self).__init__(ReadDataByPeriodicIdentifier)
