from __future__ import absolute_import
from . import *
from udsoncan.Response import Response
from udsoncan.exceptions import *

class ResponseOnEvent(BaseService):
    _sid = 0x86

    supported_negative_response = [	Response.Code.SubFunctionNotSupported, 
                                                    Response.Code.IncorrectMessageLengthOrInvalidFormat,
                                                    Response.Code.ConditionsNotCorrect,
                                                    Response.Code.RequestOutOfRange
                                                    ]

    @classmethod
    def make_request(cls):
        raise NotImplementedError(u'Service is not implemented')

    @classmethod
    def interpret_response(cls, response):
        raise NotImplementedError(u'Service is not implemented')

    class ResponseData(BaseResponseData):	
        def __init__(self):
            super(ResponseOnEvent.ResponseData, self).__init__(ResponseOnEvent)
