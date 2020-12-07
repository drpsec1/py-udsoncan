latest_standard = 2020

default_client_config  = {
        u'exception_on_negative_response'	: True,	
        u'exception_on_invalid_response'		: True,
        u'exception_on_unexpected_response'	: True,
        u'security_algo'				: None,
        u'security_algo_params'		: None,
        u'tolerate_zero_padding' 	: True,
        u'ignore_all_zero_dtc' 		: True,
        u'dtc_snapshot_did_size' 	: 2,		# Not specified in standard. 2 bytes matches other services format.
        u'server_address_format'		: None,		# 8,16,24,32,40
        u'server_memorysize_format'	: None,		# 8,16,24,32,40
        u'data_identifiers' 		: {},
        u'input_output' 			: {},
        u'request_timeout'		: 5,
        u'p2_timeout'			: 1, 
        u'p2_star_timeout'		: 5,
        u'standard_version'              : latest_standard,  # 2006, 2013, 2020
        u'use_server_timing'             : True
}
