from __future__ import absolute_import
from . import *
from udsoncan.Response import Response
from udsoncan.exceptions import *

class DynamicallyDefineDataIdentifier(BaseService):
    _sid = 0x2C

    supported_negative_response = [	 Response.Code.SubFunctionNotSupported,
                                                    Response.Code.IncorrectMessageLengthOrInvalidFormat,
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
            super(DynamicallyDefineDataIdentifier.ResponseData, self).__init__(DynamicallyDefineDataIdentifier)
