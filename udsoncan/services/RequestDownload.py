from __future__ import absolute_import
from . import *
from udsoncan.Response import Response
from udsoncan.exceptions import *
import struct 

class RequestDownload(BaseService):
    _sid = 0x34
    _use_subfunction = False

    supported_negative_response = [	 Response.Code.IncorrectMessageLengthOrInvalidFormat,
                                                    Response.Code.ConditionsNotCorrect,
                                                    Response.Code.RequestOutOfRange,
                                                    Response.Code.SecurityAccessDenied,
                                                    Response.Code.UploadDownloadNotAccepted
                                                    ]
    @classmethod
    def normalize_data_format_identifier(cls, dfi):
        from udsoncan import DataFormatIdentifier
        if dfi is None:
            dfi = DataFormatIdentifier()

        if not isinstance(dfi, DataFormatIdentifier):
            raise ValueError(u'dfi must be an instance of DataFormatIdentifier')

        return dfi

    @classmethod
    def make_request(cls, memory_location, dfi=None):
        u"""
        Generates a request for RequestDownload

        :param memory_location: The address and the size of the memory block to be written.
        :type memory_location: :ref:`MemoryLocation <MemoryLocation>`

        :param dfi: Optional :ref:`DataFormatIdentifier <DataFormatIdentifier>` defining the compression and encryption scheme of the data. 
                If not specified, the default value of 00 will be used, specifying no encryption and no compression
        :type dfi: :ref:`DataFormatIdentifier <DataFormatIdentifier>`	

        :raises ValueError: If parameters are out of range, missing or wrong type
        """				
        from udsoncan import Request, MemoryLocation

        dfi = cls.normalize_data_format_identifier(dfi)

        if not isinstance(memory_location, MemoryLocation):
            raise ValueError(u'memory_location must be an instance of MemoryLocation')

        request = Request(service=cls)
        request.data=""
        request.data += dfi.get_byte()	# Data Format Identifier
        request.data += memory_location.alfid.get_byte()	# AddressAndLengthFormatIdentifier
        request.data += memory_location.get_address_bytes()
        request.data += memory_location.get_memorysize_bytes()

        return request

    @classmethod
    def interpret_response(cls, response):
        u"""
        Populates the response ``service_data`` property with an instance of :class:`RequestDownload.ResponseData<udsoncan.services.RequestDownload.ResponseData>`

        :param response: The received response to interpret
        :type response: :ref:`Response<Response>`

        :raises InvalidResponseException: If length of ``response.data`` is too short
        :raises NotImplementedError: If the ``maxNumberOfBlockLength`` value is encoded over more than 8 bytes.
        """		

        if len(response.data) < 1:
            raise InvalidResponseException(response, u"Response data must be at least 1 bytes")

        lfid = int(ord(response.data[0])) >> 4

        if lfid > 8:
            raise NotImplementedError(u'This client does not support number bigger than %d bits' % (8*8))

        if len(response.data) < lfid+1:
            raise InvalidResponseException(response, u"Length of data (%d) is too short to contains the number of block of given length (%d)" % (len(response.data), lfid))

        todecode = bytearray('\x00\x00\x00\x00\x00\x00\x00\x00')
        for i in xrange(1,lfid+1):
            todecode[-i] = ord(response.data[lfid+1-i])

        response.service_data = cls.ResponseData()
        response.service_data.max_length = struct.unpack(u'>q', todecode)[0]

    class ResponseData(BaseResponseData):
        u"""
        .. data:: max_length

                (int) Maximum number of data blocks to write
        """		
        def __init__(self):
            super(RequestDownload.ResponseData, self).__init__(RequestDownload)
            self.max_length = None
