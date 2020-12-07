from __future__ import absolute_import
from . import *
from udsoncan.Response import Response
from udsoncan.exceptions import *
import struct

class RoutineControl(BaseService):
    _sid = 0x31

    class ControlType(BaseSubfunction):
        u"""
        RoutineControl defined subfunctions
        """		
        __pretty_name__ = u'control type'

        startRoutine = 1
        stopRoutine = 2
        requestRoutineResults = 3

    supported_negative_response = [	 Response.Code.SubFunctionNotSupported,
                                                    Response.Code.IncorrectMessageLengthOrInvalidFormat,
                                                    Response.Code.ConditionsNotCorrect,
                                                    Response.Code.RequestSequenceError,
                                                    Response.Code.RequestOutOfRange,
                                                    Response.Code.SecurityAccessDenied,
                                                    Response.Code.GeneralProgrammingFailure
                                                    ]

    @classmethod
    def make_request(cls, routine_id, control_type, data=None):
        u"""
        Generates a request for RoutineControl

        :param routine_id: The routine ID. Value should be between 0 and 0xFFFF
        :type routine_id: int

        :param control_type: Service subfunction. Allowed values are from 0 to 0x7F
        :type control_type: bytes

        :param data: Optional additional data to provide to the server
        :type data: bytes

        :raises ValueError: If parameters are out of range, missing or wrong type
        """		
        from udsoncan import Request

        ServiceHelper.validate_int(routine_id, min=0, max=0xFFFF, name=u'Routine ID')
        ServiceHelper.validate_int(control_type, min=0, max=0x7F, name=u'Routine control type')

        if data is not None:
            if not isinstance(data, str):
                raise ValueError(u'data must be a valid bytes object')

        request = Request(service=cls, subfunction=control_type)
        request.data = struct.pack(u'>H', routine_id)
        if data is not None:
            request.data += data

        return request

    @classmethod
    def interpret_response(cls, response):
        u"""
        Populates the response ``service_data`` property with an instance of :class:`RoutineControl.ResponseData<udsoncan.services.RoutineControl.ResponseData>`

        :param response: The received response to interpret
        :type response: :ref:`Response<Response>`

        :raises InvalidResponseException: If length of ``response.data`` is too short
        """

        if len(response.data) < 3: 	
            raise InvalidResponseException(response, u"Response data must be at least 3 bytes")

        response.service_data = cls.ResponseData()
        response.service_data.control_type_echo = ord(response.data[0])
        response.service_data.routine_id_echo = struct.unpack(u">H", response.data[1:3])[0]
        response.service_data.routine_status_record = response.data[3:] if len(response.data) >3 else ''

    class ResponseData(BaseResponseData):
        u"""
        .. data:: control_type_echo

                Requests subfunction echoed back by the server

        .. data:: routine_id_echo

                Requests routine ID echoed back by the server.

        .. data:: routine_status_record

                Additional data associated with the response.
        """		
        def __init__(self):
            super(RoutineControl.ResponseData, self).__init__(RoutineControl)

            self.control_type_echo = None
            self.routine_id_echo = None
            self.routine_status_record = None

