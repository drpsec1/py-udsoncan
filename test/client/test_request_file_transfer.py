from __future__ import with_statement
from __future__ import absolute_import
from udsoncan.client import Client
from udsoncan import services, DataFormatIdentifier, Filesize
from udsoncan.exceptions import *

from test.ClientServerTest import ClientServerTest

class TestRequestFileTransfer(ClientServerTest):
    def __init__(self, *args, **kwargs):
        ClientServerTest.__init__(self, *args, **kwargs)

    #============== Add File ================

    def test_add_file_success(self):
        request = self.conn.touserqueue.get(timeout=0.2)
        self.assertEqual(request, "\x38\x01\x00\x0b" + u"my_file.txt".encode(u'ascii') + "\x52\x04\x00\x00\x02\x22\x00\x00\x01\x11")
        self.conn.fromuserqueue.put("\x78\x01\x02\xab\xcd\x52")	# Positive response

    def _test_add_file_success(self):
        response = self.udsclient.add_file(u"my_file.txt", dfi= DataFormatIdentifier(compression=5, encryption=2), filesize = Filesize(uncompressed=0x222, compressed=0x111, width=4))
        self.assertTrue(response.valid)
        self.assertTrue(response.positive)
        self.assertEqual(response.service_data.moop_echo, 1)
        self.assertEqual(response.service_data.max_length, 0xabcd)
        self.assertEqual(response.service_data.dfi.compression, 5)
        self.assertEqual(response.service_data.dfi.encryption, 2)
        self.assertIsNone(response.service_data.filesize)     # No filesize info when doing AddFile. Only for ReadFile
        self.assertIsNone(response.service_data.dirinfo_length)

    def test_add_file_bad_moop_echo(self):
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78\x02\x02\xab\xcd\x00")

    def _test_add_file_bad_moop_echo(self):
        with self.assertRaises(UnexpectedResponseException):
            self.udsclient.add_file(u"my_file.txt", filesize = 0x100)            

    def test_add_file_bad_moop_echo_no_exception(self):
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78\x02\x02\xab\xcd\x00")

    def _test_add_file_bad_moop_echo_no_exception(self):
        self.udsclient.config[u'exception_on_unexpected_response'] = False        
        response = self.udsclient.add_file(u"my_file.txt", filesize = 0x100)
        self.assertTrue(response.valid)
        self.assertTrue(response.positive)
        self.assertTrue(response.unexpected)

    def test_add_file_bad_dfi(self):
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78\x01\x02\xab\xcd\x11")

    def _test_add_file_bad_dfi(self):
        with self.assertRaises(UnexpectedResponseException):
            self.udsclient.add_file(u"my_file.txt", dfi= DataFormatIdentifier(compression=5, encryption=2), filesize = 0x100)

    def test_add_file_zerolen_length(self):
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78\x01\x00\x00")

    def _test_add_file_zerolen_length(self):
        with self.assertRaises(InvalidResponseException):
            self.udsclient.add_file(u"my_file.txt", filesize = 0x100)

    def test_add_file_negative_response(self):
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x7F\x38\x22")    # Condition not correct

    def _test_add_file_negative_response(self):
        with self.assertRaises(NegativeResponseException):
            self.udsclient.add_file(u"my_file.txt", filesize=0x100)

    def test_add_file_negative_response_no_exception(self):
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x7F\x38\x22")    # Condition not correct

    def _test_add_file_negative_response_no_exception(self):
        self.udsclient.config[u'exception_on_negative_response'] = False
        response = self.udsclient.add_file(u"my_file.txt", filesize=0x100)
        self.assertTrue(response.valid)
        self.assertFalse(response.positive)

    def test_add_file_invalid_length(self):
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78")   
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78\x01")    
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78\x01\x02")
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78\x01\x02\xab")
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78\x01\x02\xab\xcd")

    def _test_add_file_invalid_length(self):
        for i in xrange(5):
            with self.assertRaises(InvalidResponseException):
                self.udsclient.add_file(u"my_file.txt", filesize = 0x100)

    def test_add_file_extra_bytes_response(self):
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78\x01\x02\xab\xcd\x52\xAA")    # Positive response

    def _test_add_file_extra_bytes_response(self):
        with self.assertRaises(InvalidResponseException):
            self.udsclient.add_file(u"my_file.txt", dfi= DataFormatIdentifier(compression=5, encryption=2), filesize = Filesize(uncompressed=0x222, compressed=0x111, width=4))

    def test_add_file_extra_bytes_response_zero_padding_ok(self):
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78\x01\x02\xab\xcd\x52\x00")    # Positive response

    def _test_add_file_extra_bytes_response_zero_padding_ok(self):
        self.udsclient.config[u'tolerate_zero_padding'] = True
        response = self.udsclient.add_file(u"my_file.txt", dfi= DataFormatIdentifier(compression=5, encryption=2), filesize = Filesize(uncompressed=0x222, compressed=0x111, width=4))
        self.assertTrue(response.valid)
        self.assertTrue(response.positive)
        self.assertEqual(response.service_data.moop_echo, 1)
        self.assertEqual(response.service_data.max_length, 0xabcd)
        self.assertEqual(response.service_data.dfi.compression, 5)
        self.assertEqual(response.service_data.dfi.encryption, 2)
        self.assertIsNone(response.service_data.filesize)     # No filesize info when doing AddFile. Only for ReadFile
        self.assertIsNone(response.service_data.dirinfo_length)

    def test_add_file_extra_bytes_response_zero_padding_not_ok(self):
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78\x01\x02\xab\xcd\x52\x00")    # Positive response

    def _test_add_file_extra_bytes_response_zero_padding_not_ok(self):
        self.udsclient.config[u'tolerate_zero_padding'] = False
        with self.assertRaises(InvalidResponseException):
            self.udsclient.add_file(u"my_file.txt", dfi= DataFormatIdentifier(compression=5, encryption=2), filesize = Filesize(uncompressed=0x222, compressed=0x111, width=4))


    #============== Delete File ================

    def test_delete_file_success(self):
        request = self.conn.touserqueue.get(timeout=0.2)
        self.assertEqual(request, "\x38\x02\x00\x0b" + u"my_file.txt".encode(u'ascii'))
        self.conn.fromuserqueue.put("\x78\x02")    # Positive response

    def _test_delete_file_success(self):
        response = self.udsclient.delete_file(u"my_file.txt")
        self.assertTrue(response.valid)
        self.assertTrue(response.positive)
        self.assertEqual(response.service_data.moop_echo, 2)
        self.assertIsNone(response.service_data.max_length)
        self.assertIsNone(response.service_data.dfi)
        self.assertIsNone(response.service_data.filesize)
        self.assertIsNone(response.service_data.dirinfo_length)

    def test_delete_bad_moop_echo(self):
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78\x03")    # Positive response

    def _test_delete_bad_moop_echo(self):
        with self.assertRaises(UnexpectedResponseException):
            self.udsclient.delete_file(u"my_file.txt")

    def test_delete_bad_moop_echo_no_exception(self):
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78\x03")    # Positive response

    def _test_delete_bad_moop_echo_no_exception(self):
        self.udsclient.config[u'exception_on_unexpected_response'] = False        
        response = self.udsclient.delete_file(u"my_file.txt")
        self.assertTrue(response.valid)
        self.assertTrue(response.positive)
        self.assertTrue(response.unexpected)

    def test_delete_file_negative_response(self):
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x7F\x38\x22")    # Condition not correct

    def _test_delete_file_negative_response(self):
        with self.assertRaises(NegativeResponseException):
            self.udsclient.delete_file(u"my_file.txt")

    def test_delete_file_negative_response_no_exception(self):
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x7F\x38\x22")    # Condition not correct

    def _test_delete_file_negative_response_no_exception(self):
        self.udsclient.config[u'exception_on_negative_response'] = False
        response = self.udsclient.delete_file(u"my_file.txt")
        self.assertTrue(response.valid)
        self.assertFalse(response.positive)  

    def test_delete_file_extra_bytes_response(self):
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78\x02\xAA")    # Positive response

    def _test_delete_file_extra_bytes_response(self):
        with self.assertRaises(InvalidResponseException):
            self.udsclient.delete_file(u"my_file.txt")

    def test_delete_file_extra_bytes_response_zero_padding_ok(self):
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78\x02\x00\x00")    # Positive response

    def _test_delete_file_extra_bytes_response_zero_padding_ok(self):
        self.udsclient.config[u'tolerate_zero_padding'] = True
        response = self.udsclient.delete_file(u"my_file.txt")
        self.assertTrue(response.valid)
        self.assertTrue(response.positive)
        self.assertEqual(response.service_data.moop_echo, 2)
        self.assertIsNone(response.service_data.max_length)
        self.assertIsNone(response.service_data.dfi)
        self.assertIsNone(response.service_data.filesize)
        self.assertIsNone(response.service_data.dirinfo_length)

    def test_delete_file_extra_bytes_response_zero_padding_not_ok(self):
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78\x02\x00\x00")    # Positive response

    def _test_delete_file_extra_bytes_response_zero_padding_not_ok(self):
        self.udsclient.config[u'tolerate_zero_padding'] = False
        with self.assertRaises(InvalidResponseException):
            self.udsclient.delete_file(u"my_file.txt")


    #============== Replace File ================

    def test_replace_file_success(self):
        request = self.conn.touserqueue.get(timeout=0.2)
        self.assertEqual(request, "\x38\x03\x00\x0b" + u"my_file.txt".encode(u'ascii') + "\x52\x04\x00\x00\x02\x22\x00\x00\x01\x11")
        self.conn.fromuserqueue.put("\x78\x03\x02\xab\xcd\x52")    # Positive response

    def _test_replace_file_success(self):
        response = self.udsclient.replace_file(u"my_file.txt", dfi= DataFormatIdentifier(compression=5, encryption=2), filesize = Filesize(uncompressed=0x222, compressed=0x111, width=4))
        self.assertTrue(response.valid)
        self.assertTrue(response.positive)
        self.assertEqual(response.service_data.moop_echo, 3)
        self.assertEqual(response.service_data.max_length, 0xabcd)
        self.assertEqual(response.service_data.dfi.compression, 5)
        self.assertEqual(response.service_data.dfi.encryption, 2)
        self.assertIsNone(response.service_data.filesize)     # No filesize info when doing AddFile. Only for ReadFile
        self.assertIsNone(response.service_data.dirinfo_length)

    def test_replace_file_negative_response(self):
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x7F\x38\x22")    # Condition not correct

    def _test_replace_file_negative_response(self):
        with self.assertRaises(NegativeResponseException):
            self.udsclient.replace_file(u"my_file.txt", dfi= DataFormatIdentifier(compression=5, encryption=2), filesize = Filesize(uncompressed=0x222, compressed=0x111, width=4))

    def test_replace_file_negative_response_no_exception(self):
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x7F\x38\x22")    # Condition not correct

    def _test_replace_file_negative_response_no_exception(self):
        self.udsclient.config[u'exception_on_negative_response'] = False
        response = self.udsclient.replace_file(u"my_file.txt", dfi= DataFormatIdentifier(compression=5, encryption=2), filesize = Filesize(uncompressed=0x222, compressed=0x111, width=4))
        self.assertTrue(response.valid)
        self.assertFalse(response.positive)           

    def test_replace_file_bad_moop_echo(self):
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78\x02\x02\xab\xcd\x00")

    def _test_replace_file_bad_moop_echo(self):
        with self.assertRaises(UnexpectedResponseException):
            self.udsclient.replace_file(u"my_file.txt", filesize = 0x100)            

    def test_replace_file_bad_moop_echo_no_exception(self):
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78\x02\x02\xab\xcd\x00")

    def _test_replace_file_bad_moop_echo_no_exception(self):
        self.udsclient.config[u'exception_on_unexpected_response'] = False        
        response = self.udsclient.replace_file(u"my_file.txt", filesize = 0x100)
        self.assertTrue(response.valid)
        self.assertTrue(response.positive)
        self.assertTrue(response.unexpected)

    def test_replace_file_bad_dfi(self):
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78\x03\x02\xab\xcd\x11")

    def _test_replace_file_bad_dfi(self):
        with self.assertRaises(UnexpectedResponseException):
            self.udsclient.replace_file(u"my_file.txt", dfi= DataFormatIdentifier(compression=5, encryption=2), filesize = 0x100)

    def test_replace_file_zerolen_length(self):
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78\x03\x00\x00")

    def _test_replace_file_zerolen_length(self):
        with self.assertRaises(InvalidResponseException):
            self.udsclient.replace_file(u"my_file.txt", filesize = 0x100)

    def test_replace_file_negative_response(self):
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x7F\x38\x22")    # Condition not correct

    def _test_replace_file_negative_response(self):
        with self.assertRaises(NegativeResponseException):
            self.udsclient.replace_file(u"my_file.txt", filesize=0x100)

    def test_replace_file_negative_response_no_exception(self):
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x7F\x38\x22")    # Condition not correct

    def _test_replace_file_negative_response_no_exception(self):
        self.udsclient.config[u'exception_on_negative_response'] = False
        response = self.udsclient.replace_file(u"my_file.txt", filesize=0x100)
        self.assertTrue(response.valid)
        self.assertFalse(response.positive)

    def test_replace_file_invalid_length(self):
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78")   
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78\x03")    
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78\x03\x02")
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78\x03\x02\xab")
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78\x03\x02\xab\xcd")

    def _test_replace_file_invalid_length(self):
        for i in xrange(5):
            with self.assertRaises(InvalidResponseException):
                self.udsclient.replace_file(u"my_file.txt", filesize = 0x100)

    def test_replace_file_extra_bytes_response(self):
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78\x03\x02\xab\xcd\x52\xAA")    # Positive response

    def _test_replace_file_extra_bytes_response(self):
        with self.assertRaises(InvalidResponseException):
            self.udsclient.replace_file(u"my_file.txt", dfi= DataFormatIdentifier(compression=5, encryption=2), filesize = Filesize(uncompressed=0x222, compressed=0x111, width=4))              

    def test_replace_file_extra_bytes_response_zero_padding_ok(self):
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78\x03\x02\xab\xcd\x52\x00\x00")    # Positive response

    def _test_replace_file_extra_bytes_response_zero_padding_ok(self):
        self.udsclient.config[u'tolerate_zero_padding'] = True
        response = self.udsclient.replace_file(u"my_file.txt", dfi= DataFormatIdentifier(compression=5, encryption=2), filesize = Filesize(uncompressed=0x222, compressed=0x111, width=4))              
        self.assertTrue(response.valid)
        self.assertTrue(response.positive)
        self.assertEqual(response.service_data.moop_echo, 3)
        self.assertEqual(response.service_data.max_length, 0xabcd)
        self.assertEqual(response.service_data.dfi.compression, 5)
        self.assertEqual(response.service_data.dfi.encryption, 2)
        self.assertIsNone(response.service_data.filesize)     # No filesize info when doing AddFile. Only for ReadFile
        self.assertIsNone(response.service_data.dirinfo_length)

    def test_replace_file_extra_bytes_response_zero_padding_not_ok(self):
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78\x03\x02\xab\xcd\x52\x00")    # Positive response

    def _test_replace_file_extra_bytes_response_zero_padding_not_ok(self):
        self.udsclient.config[u'tolerate_zero_padding'] = False
        with self.assertRaises(InvalidResponseException):
            self.udsclient.replace_file(u"my_file.txt", dfi= DataFormatIdentifier(compression=5, encryption=2), filesize = Filesize(uncompressed=0x222, compressed=0x111, width=4))              

    #============== Read File ================

    def test_read_file_success(self):
        request = self.conn.touserqueue.get(timeout=0.2)
        self.assertEqual(request, "\x38\x04\x00\x0b" + u"my_file.txt".encode(u'ascii') + "\x52")
        self.conn.fromuserqueue.put("\x78\x04\x02\xab\xcd\x52\x00\x02\x98\x76\x12\x34")    # Positive response

    def _test_read_file_success(self):
        response = self.udsclient.read_file(u"my_file.txt", dfi= DataFormatIdentifier(compression=5, encryption=2))
        self.assertTrue(response.valid)
        self.assertTrue(response.positive)
        self.assertEqual(response.service_data.moop_echo, 4)
        self.assertEqual(response.service_data.max_length, 0xabcd)
        self.assertEqual(response.service_data.dfi.compression, 5)
        self.assertEqual(response.service_data.dfi.encryption, 2)
        self.assertEqual(response.service_data.filesize.uncompressed, 0x9876)
        self.assertEqual(response.service_data.filesize.compressed, 0x1234)
        self.assertIsNone(response.service_data.dirinfo_length)

    def test_read_file_negative_response(self):
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x7F\x38\x22")    # Condition not correct

    def _test_read_file_negative_response(self):
        with self.assertRaises(NegativeResponseException):
            self.udsclient.read_file(u"my_file.txt", dfi= DataFormatIdentifier(compression=5, encryption=2))

    def test_read_file_negative_response_no_exception(self):
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x7F\x38\x22")    # Condition not correct

    def _test_read_file_negative_response_no_exception(self):
        self.udsclient.config[u'exception_on_negative_response'] = False
        response = self.udsclient.read_file(u"my_file.txt", dfi= DataFormatIdentifier(compression=5, encryption=2))
        self.assertTrue(response.valid)
        self.assertFalse(response.positive)           

    def test_read_file_bad_moop_echo(self):
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78\x05\x02\xab\xcd\x52\x00\x02\x98\x76\x12\x34")

    def _test_read_file_bad_moop_echo(self):
        with self.assertRaises(UnexpectedResponseException):
            self.udsclient.read_file(u"my_file.txt", dfi= DataFormatIdentifier(compression=5, encryption=2))

    def test_read_file_bad_moop_echo_no_exception(self):
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78\x05\x02\xab\xcd\x52\x00\x02\x98\x76\x12\x34")

    def _test_read_file_bad_moop_echo_no_exception(self):
        self.udsclient.config[u'exception_on_unexpected_response'] = False        
        response = self.udsclient.read_file(u"my_file.txt", dfi= DataFormatIdentifier(compression=5, encryption=2))
        self.assertTrue(response.valid)
        self.assertTrue(response.positive)
        self.assertTrue(response.unexpected)

    def test_read_file_bad_dfi(self):
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78\x04\x02\xab\xcd\x11\x00\x02\x98\x76\x12\x34")

    def _test_read_file_bad_dfi(self):
        with self.assertRaises(UnexpectedResponseException):
            self.udsclient.read_file(u"my_file.txt", dfi= DataFormatIdentifier(compression=5, encryption=2))

    def test_read_file_zerolen_length_lfi(self):
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78\x04\x00\x52\x00\x02\x98\x76\x12\x34")

    def _test_read_file_zerolen_length_lfi(self):
        with self.assertRaises(InvalidResponseException):
            self.udsclient.read_file(u"my_file.txt", dfi= DataFormatIdentifier(compression=5, encryption=2))

    def test_read_file_zerolen_length_fsodipl(self):
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78\x04\x02\xab\xcd\x52\x00\x00")

    def _test_read_file_zerolen_length_fsodipl(self):
        with self.assertRaises(InvalidResponseException):
            self.udsclient.read_file(u"my_file.txt", dfi= DataFormatIdentifier(compression=5, encryption=2))            

    def test_read_file_invalid_length(self):
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78")
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78\x04")
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78\x04\x02")
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78\x04\x02\xab")
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78\x04\x02\xab\xcd")
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78\x04\x02\xab\xcd\x52")
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78\x04\x02\xab\xcd\x52\x00")
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78\x04\x02\xab\xcd\x52\x00\x02")
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78\x04\x02\xab\xcd\x52\x00\x02\x98")
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78\x04\x02\xab\xcd\x52\x00\x02\x98\x76")
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78\x04\x02\xab\xcd\x52\x00\x02\x98\x76\x12")

    def _test_read_file_invalid_length(self):
        for i in xrange(11):
            with self.assertRaises(InvalidResponseException):
                self.udsclient.read_file(u"my_file.txt", dfi= DataFormatIdentifier(compression=5, encryption=2))

    def test_read_file_extra_bytes_response(self):
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78\x04\x02\xab\xcd\x52\x00\x02\x98\x76\x12\x34\xAA")    # Positive response

    def _test_read_file_extra_bytes_response(self):
        with self.assertRaises(InvalidResponseException):
            self.udsclient.read_file(u"my_file.txt", dfi= DataFormatIdentifier(compression=5, encryption=2))

    def test_read_file_extra_bytes_response_zero_padding_ok(self):
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78\x04\x02\xab\xcd\x52\x00\x02\x98\x76\x12\x34\x00")    # Positive response

    def _test_read_file_extra_bytes_response_zero_padding_ok(self):
        self.udsclient.config[u'tolerate_zero_padding'] = True
        response = self.udsclient.read_file(u"my_file.txt", dfi= DataFormatIdentifier(compression=5, encryption=2))
        self.assertTrue(response.valid)
        self.assertTrue(response.positive)
        self.assertEqual(response.service_data.moop_echo, 4)
        self.assertEqual(response.service_data.max_length, 0xabcd)
        self.assertEqual(response.service_data.dfi.compression, 5)
        self.assertEqual(response.service_data.dfi.encryption, 2)
        self.assertEqual(response.service_data.filesize.uncompressed, 0x9876)
        self.assertEqual(response.service_data.filesize.compressed, 0x1234)
        self.assertIsNone(response.service_data.dirinfo_length)

    def test_read_file_extra_bytes_response_zero_padding_not_ok(self):
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78\x04\x02\xab\xcd\x52\x00\x02\x98\x76\x12\x34\x00")    # Positive response

    def _test_read_file_extra_bytes_response_zero_padding_not_ok(self):
        self.udsclient.config[u'tolerate_zero_padding'] = False
        with self.assertRaises(InvalidResponseException):
            self.udsclient.read_file(u"my_file.txt", dfi= DataFormatIdentifier(compression=5, encryption=2))


    #============== Read Directory ================

    def test_read_dir_success(self):
        request = self.conn.touserqueue.get(timeout=0.2)
        self.assertEqual(request, "\x38\x05\x00\x0c" + u"/path/to/dir".encode(u'ascii'))
        self.conn.fromuserqueue.put("\x78\x05\x02\xab\xcd\x00\x00\x02\x12\x34")    # Positive response

    def _test_read_dir_success(self):
        response = self.udsclient.read_dir(u"/path/to/dir")
        self.assertTrue(response.valid)
        self.assertTrue(response.positive)
        self.assertEqual(response.service_data.moop_echo, 5)
        self.assertEqual(response.service_data.max_length, 0xabcd)
        self.assertEqual(response.service_data.dfi.encryption, 0)
        self.assertEqual(response.service_data.dfi.compression, 0)
        self.assertIsNone(response.service_data.filesize)
        self.assertEqual(response.service_data.dirinfo_length, 0x1234)

    def test_read_dir_negative_response(self):
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x7F\x38\x22")    # Condition not correct

    def _test_read_dir_negative_response(self):
        with self.assertRaises(NegativeResponseException):
            self.udsclient.read_dir(u"/path/to/dir")

    def test_read_dir_negative_response_no_exception(self):
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x7F\x38\x22")    # Condition not correct

    def _test_read_dir_negative_response_no_exception(self):
        self.udsclient.config[u'exception_on_negative_response'] = False
        response = self.udsclient.read_dir(u"/path/to/dir")
        self.assertTrue(response.valid)
        self.assertFalse(response.positive)          

    def test_read_dir_bad_moop_echo(self):
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78\x01\x02\xab\xcd\x00\x00\x02\x12\x34")    # Positive response

    def _test_read_dir_bad_moop_echo(self):
        with self.assertRaises(UnexpectedResponseException):
            self.udsclient.read_dir(u"/path/to/dir")

    def test_read_dir_bad_moop_echo_no_exception(self):
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78\x01\x02\xab\xcd\x00\x00\x02\x12\x34")    # Positive response

    def _test_read_dir_bad_moop_echo_no_exception(self):
        self.udsclient.config[u'exception_on_unexpected_response'] = False        
        response = self.udsclient.read_dir(u"/path/to/dir")
        self.assertTrue(response.valid)
        self.assertTrue(response.positive)
        self.assertTrue(response.unexpected)

    def test_read_dir_dfi_not_zero(self):
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78\x05\x02\xab\xcd\x52\x00\x02\x12\x34")    # Positive response

    def _test_read_dir_dfi_not_zero(self):
        with self.assertRaises(InvalidResponseException):
            self.udsclient.read_dir(u"/path/to/dir")

    def test_read_dir_zerolen_length_lfi(self):
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78\x05\x00\x00\x00\x02\x12\x34")

    def _test_read_dir_zerolen_length_lfi(self):
        with self.assertRaises(InvalidResponseException):
            self.udsclient.read_dir(u"/path/to/dir")

    def test_read_dir_zerolen_length_fsodipl(self):
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78\x05\x02\xab\xcd\x00\x00\x00")

    def _test_read_dir_zerolen_length_fsodipl(self):
        with self.assertRaises(InvalidResponseException):
            self.udsclient.read_dir(u"/path/to/dir")

    def test_read_dir_invalid_length(self):
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78")
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78\x05")
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78\x05\x02")
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78\x05\x02\xab")
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78\x05\x02\xab\xcd")
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78\x05\x02\xab\xcd\x00")
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78\x05\x02\xab\xcd\x00\x00")
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78\x05\x02\xab\xcd\x00\x00\x02")
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78\x05\x02\xab\xcd\x00\x00\x02\x12")

    def _test_read_dir_invalid_length(self):
        for i in xrange(9):
            with self.assertRaises(InvalidResponseException):
                self.udsclient.read_dir(u"/path/to/dir")

    def test_read_dir_extra_bytes_response(self):
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78\x05\x02\xab\xcd\x00\x00\x02\x12\x34\xAA")    # Positive response

    def _test_read_dir_extra_bytes_response(self):
        with self.assertRaises(InvalidResponseException):
            response = self.udsclient.read_dir(u"/path/to/dir")

    def test_read_dir_extra_bytes_response_zero_padding_ok(self):
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78\x05\x02\xab\xcd\x00\x00\x02\x12\x34\x00")    # Positive response

    def _test_read_dir_extra_bytes_response_zero_padding_ok(self):
        self.udsclient.config[u'tolerate_zero_padding'] = True
        response = response = self.udsclient.read_dir(u"/path/to/dir")
        self.assertTrue(response.valid)
        self.assertTrue(response.positive)
        self.assertEqual(response.service_data.moop_echo, 5)
        self.assertEqual(response.service_data.max_length, 0xabcd)
        self.assertEqual(response.service_data.dfi.compression, 0)
        self.assertEqual(response.service_data.dfi.encryption, 0)
        self.assertIsNone(response.service_data.filesize)
        self.assertEqual(response.service_data.dirinfo_length, 0x1234)

    def test_read_dir_extra_bytes_response_zero_padding_not_ok(self):
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x78\x05\x02\xab\xcd\x00\x00\x02\x12\x34\x00")    # Positive response

    def _test_read_dir_extra_bytes_response_zero_padding_not_ok(self):
        self.udsclient.config[u'tolerate_zero_padding'] = False
        with self.assertRaises(InvalidResponseException):
            response = self.udsclient.read_dir(u"/path/to/dir")


    # ============= Misc ==========================

    def test_wrong_service_reply(self):
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x71\x01\x02\xab\xcd\x00")   # Reply service ID of routine control

    def _test_wrong_service_reply(self):
        with self.assertRaises(UnexpectedResponseException):
            self.udsclient.add_file(u"my_file.txt", filesize = 0x100)

    def test_wrong_service_reply_no_exception(self):
        self.conn.touserqueue.get(timeout=0.2)
        self.conn.fromuserqueue.put("\x71\x01\x02\xab\xcd\x00")   # Reply service ID of routine control

    def _test_wrong_service_reply_no_exception(self):
        self.udsclient.config[u'exception_on_unexpected_response'] = False
        response = self.udsclient.add_file(u"my_file.txt", filesize=0x100)
        self.assertTrue(response.valid)
        self.assertTrue(response.unexpected)

    def test_default_dfi(self):
        request = self.conn.touserqueue.get(timeout=0.2)
        self.assertEqual(request, "\x38\x01\x00\x0b" + u"my_file.txt".encode(u'ascii') + "\x00\x04\x00\x00\x02\x22\x00\x00\x01\x11")
        self.conn.fromuserqueue.put("\x78\x01\x02\xab\xcd\x00")    # Positive response

    def _test_default_dfi(self):
        response = self.udsclient.request_file_transfer(moop=1, path=u"my_file.txt", filesize = Filesize(uncompressed=0x222, compressed=0x111, width=4))
        self.assertEqual(response.service_data.dfi.compression, 0)
        self.assertEqual(response.service_data.dfi.encryption, 0)

    def test_default_filesize_width(self):
        request = self.conn.touserqueue.get(timeout=0.2)
        self.assertEqual(request, "\x38\x01\x00\x0b" + u"my_file.txt".encode(u'ascii') + "\x00\x02\x02\x22\x01\x11")
        self.conn.fromuserqueue.put("\x78\x01\x02\xab\xcd\x00")    # Positive response

    def _test_default_filesize_width(self):
        self.udsclient.request_file_transfer(moop=1, path=u"my_file.txt", filesize = Filesize(uncompressed=0x222, compressed=0x111))

    def test_filesize_no_compressed_size(self):
        request = self.conn.touserqueue.get(timeout=0.2)
        self.assertEqual(request, "\x38\x01\x00\x0b" + u"my_file.txt".encode(u'ascii') + "\x00\x04\x00\x00\x02\x22\x00\x00\x02\x22")
        self.conn.fromuserqueue.put("\x78\x01\x02\xab\xcd\x00")    # Positive response

    def _test_filesize_no_compressed_size(self):
        self.udsclient.request_file_transfer(moop=1, path=u"my_file.txt", filesize = Filesize(uncompressed=0x222, width=4))

    def test_filesize_numerical(self):
        request = self.conn.touserqueue.get(timeout=0.2)
        self.assertEqual(request, "\x38\x01\x00\x0b" + u"my_file.txt".encode(u'ascii') + "\x00\x02\x01\x00\x01\x00")
        self.conn.fromuserqueue.put("\x78\x01\x02\xab\xcd\x00")    # Positive response

    def _test_filesize_numerical(self):
        self.udsclient.request_file_transfer(moop=1, path=u"my_file.txt", filesize = 0x100)

    def test_bad_param(self):
        request = None
        try:
            self.conn.touserqueue.get(timeout=0.2)
        except:
            pass
        self.assertIsNone(request)

    def _test_bad_param(self):
        good_filesize = Filesize(uncompressed=0x222, compressed=0x111, width=4)
        good_dfi = DataFormatIdentifier(compression=5, encryption=2)
        with self.assertRaises(ValueError):
            self.udsclient.request_file_transfer(moop=1, path=u"a"*(2**16), dfi=good_dfi, filesize = good_filesize)

        with self.assertRaises(ValueError):
            self.udsclient.request_file_transfer(moop=1, path=u"", dfi=good_dfi, filesize = good_filesize)

        with self.assertRaises(ValueError):
            self.udsclient.request_file_transfer(moop=1, path=u"hello.txt", dfi=1, filesize = good_filesize)

        with self.assertRaises(ValueError):
            self.udsclient.request_file_transfer(moop=1, path=u"hello.txt", dfi=good_dfi, filesize = u"asd")

        for moop in [2, 4, 5]:  # Delete File, Read File, Read Dir
            with self.assertRaises(ValueError):
                self.udsclient.request_file_transfer(moop=moop, path=u"hello.txt", dfi=good_dfi, filesize = good_filesize)   # unexpected filesize

        for moop in [1, 3]: # Add File, Replace File
            with self.assertRaises(ValueError):
                self.udsclient.request_file_transfer(moop=moop, path=u"hello.txt", dfi=good_dfi, filesize = None)    # missing filesize

        for moop in [2, 5]:
            with self.assertRaises(ValueError):
                self.udsclient.request_file_transfer(moop=moop, path=u"hello.txt", dfi=good_dfi, filesize = None)    # dfi not expected
