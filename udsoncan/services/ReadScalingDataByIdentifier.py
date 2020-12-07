from __future__ import absolute_import
from . import *
from udsoncan.Response import Response
from udsoncan.exceptions import *

class ReadScalingDataByIdentifier(BaseService):
    _sid = 0x24

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
            super(ReadScalingDataByIdentifier.ResponseData, self).__init__(ReadScalingDataByIdentifier)
