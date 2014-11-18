"""
    ZPI command and commands structure module
"""

__all__ = ['ZpiCommand', 'ZpiCommands']

class ZpiCommand(object):
    """ ZPI command enumeration class """
    
    #Request command enumerations ->
    SYS_RESET_REQ = 'SYS_RESET_REQ'
    SYS_VERSION = 'SYS_VERSION'
    SYS_OSAL_NV_READ = 'SYS_OSAL_NV_READ'
    SYS_OSAL_NV_WRITE = 'SYS_OSAL_NV_WRITE'
    SYS_OSAL_NV_ITEM_INIT = 'SYS_OSAL_NV_ITEM_INIT'
    SYS_OSAL_NV_DELETE = 'SYS_OSAL_NV_DELETE'
    SYS_OSAL_NV_LENGTH = 'SYS_OSAL_NV_LENGTH'
    SYS_ADC_READ = 'SYS_ADC_READ'
    SYS_GPIO = 'SYS_GPIO'
    SYS_RANDOM = 'SYS_RANDOM'
    SYS_SET_TIME = 'SYS_SET_TIME'
    SYS_GET_TIME = 'SYS_GET_TIME'
    SYS_SET_TX_POWER = 'SYS_SET_TX_POWER'
    ZB_READ_CONFIGURATION = 'ZB_READ_CONFIGURATION'
    ZB_WRITE_CONFIGURATION = 'ZB_WRITE_CONFIGURATION'
    ZB_APP_REGISTER_REQUEST = 'ZB_APP_REGISTER_REQUEST'
    ZB_START_REQUEST = 'ZB_START_REQUEST'
    ZB_PERMIT_JOINING_REQUEST = 'ZB_PERMIT_JOINING_REQUEST'
    ZB_BIND_DEVICE = 'ZB_BIND_DEVICE'
    ZB_ALLOW_BIND = 'ZB_ALLOW_BIND'
    ZB_SEND_DATA_REQUEST = 'ZB_SEND_DATA_REQUEST'
    ZB_GET_DEVICE_INFO = 'ZB_GET_DEVICE_INFO'
    ZB_FIND_DEVICE_REQUEST = 'ZB_FIND_DEVICE_REQUEST'
    AF_REGISTER = 'AF_REGISTER'
    AF_DATA_REQUEST = 'AF_DATA_REQUEST'
    AF_DATA_REQUEST_EXT = 'AF_DATA_REQUEST_EXT'
    AF_DATA_REQUEST_SRC_RTG = 'AF_DATA_REQUEST_SRC_RTG'
    AF_INTER_PAN_CTRL = 'AF_INTER_PAN_CTRL'
    AF_DATA_STORE = 'AF_DATA_STORE'
    AF_DATA_RETRIEVE = 'AF_DATA_RETRIEVE'
    AF_APSF_CONFIG_SET = 'AF_APSF_CONFIG_SET'
    ZDO_NWK_ADDR_REQ = 'ZDO_NWK_ADDR_REQ'
    ZDO_IEEE_ADDR_REQ = 'ZDO_IEEE_ADDR_REQ'
    ZDO_NODE_DESC_REQ = 'ZDO_NODE_DESC_REQ'
    ZDO_POWER_DESC_REQ = 'ZDO_POWER_DESC_REQ'
    ZDO_SIMPLE_DESC_REQ = 'ZDO_SIMPLE_DESC_REQ'
    ZDO_ACTIVE_EP_REQ = 'ZDO_ACTIVE_EP_REQ'
    ZDO_MATCH_DESC_REQ = 'ZDO_MATCH_DESC_REQ'
    ZDO_COMPLEX_DESC_REQ = 'ZDO_COMPLEX_DESC_REQ'
    ZDO_USER_DESC_REQ = 'ZDO_USER_DESC_REQ'
    ZDO_DEVICE_ANNCE = 'ZDO_DEVICE_ANNCE'
    ZDO_USER_DESC_SET = 'ZDO_USER_DESC_SET'
    ZDO_SERVER_DESC_REQ = 'ZDO_SERVER_DESC_REQ'
    ZDO_END_DEVICE_BIND_REQ = 'ZDO_END_DEVICE_BIND_REQ'
    ZDO_BIND_REQ = 'ZDO_BIND_REQ'
    ZDO_UNBIND_REQ = 'ZDO_UNBIND_REQ'
    ZDO_MGMT_NWK_DISC_REQ = 'ZDO_MGMT_NWK_DISC_REQ'
    ZDO_MGMT_LQI_REQ = 'ZDO_MGMT_LQI_REQ'
    ZDO_MGMT_RTG_REQ = 'ZDO_MGMT_RTG_REQ'
    ZDO_MGMT_BIND_REQ = 'ZDO_MGMT_BIND_REQ'
    ZDO_MGMT_LEAVE_REQ = 'ZDO_MGMT_LEAVE_REQ'
    ZDO_MGMT_DIRECT_JOIN_REQ = 'ZDO_MGMT_DIRECT_JOIN_REQ'
    ZDO_MGMT_PERMIT_JOIN_REQ = 'ZDO_MGMT_PERMIT_JOIN_REQ'
    ZDO_MGMT_NWK_UPDATE_REQ = 'ZDO_MGMT_NWK_UPDATE_REQ'
    ZDO_STARTUP_FROM_APP = 'ZDO_STARTUP_FROM_APP'
    ZDO_AUTO_FIND_DESTINATION = 'ZDO_AUTO_FIND_DESTINATION'
    ZDO_SET_LINK_KEY = 'ZDO_SET_LINK_KEY'
    ZDO_REMOVE_LINK_KEY = 'ZDO_REMOVE_LINK_KEY'
    ZDO_GET_LINK_KEY = 'ZDO_GET_LINK_KEY'
    ZDO_NWK_DISCOVERY_REQ = 'ZDO_NWK_DISCOVERY_REQ'
    ZDO_JOIN_REQ = 'ZDO_JOIN_REQ'
    ZDO_MSG_CB_REGISTER = 'ZDO_MSG_CB_REGISTER'
    ZDO_MSG_CB_REMOVE_REQ = 'ZDO_MSG_CB_REMOVE_REQ'
    UTIL_DATA_REQ = 'UTIL_DATA_REQ'
    UTIL_ADDRMGR_EXT_ADDR_LOOKUP = 'UTIL_ADDRMGR_EXT_ADDR_LOOKUP'
    UTIL_ADDRMGR_NWK_ADDR_LOOKUP = 'UTIL_ADDRMGR_NWK_ADDR_LOOKUP'
    UTIL_APSME_LINK_KEY_DATA_GET = 'UTIL_APSME_LINK_KEY_DATA_GET'
    UTIL_APSME_LINK_KEY_NV_ID_GET = 'UTIL_APSME_LINK_KEY_NV_ID_GET'
    UTIL_APSME_REQUEST_KEY_CMD = 'UTIL_APSME_REQUEST_KEY_CMD'
    UTIL_ASSOC_COUNT = 'UTIL_ASSOC_COUNT'
    UTIL_ASSOC_FIND_DEVICE = 'UTIL_ASSOC_FIND_DEVICE'
    UTIL_ZCL_KEY_EST_INIT_EST = 'UTIL_ZCL_KEY_EST_INIT_EST'
    UTIL_ZCL_KEY_EST_SIGN = 'UTIL_ZCL_KEY_EST_SIGN'
    UTIL_ZCL_KEY_EST_IND = 'UTIL_ZCL_KEY_EST_IND'
    UTIL_TEST_LOOPBACK = 'UTIL_TEST_LOOPBACK'
    
    #APS Expanded 
    APS_ADD_GROUP = 'APS_ADD_GROUP'
    APS_REMOVE_GROUP = 'APS_REMOVE_GROUP'
    APS_REMOVE_ALL_GROUP = 'APS_REMOVE_ALL_GROUP'
    APS_FIND_GROUP = 'APS_FIND_GROUP'
    APS_FIND_ALL_GROUPS_FOR_EP = 'APS_FIND_ALL_GROUPS_FOR_EP'
    APS_COUNT_ALL_GROUPS = 'APS_COUNT_ALL_GROUPS'    
    
    #response command enumerations
    SYS_RESET_IND = 'SYS_RESET_IND'
    SYS_VERSION_SRSP = 'SYS_VERSION_SRSP'
    SYS_OSAL_NV_READ_SRSP = 'SYS_OSAL_NV_READ_SRSP'
    SYS_OSAL_NV_WRITE_SRSP = 'SYS_OSAL_NV_WRITE_SRSP'
    SYS_OSAL_NV_ITEM_INIT_SRSP = 'SYS_OSAL_NV_ITEM_INIT_SRSP'
    SYS_OSAL_NV_DELETE_SRSP = 'SYS_OSAL_NV_DELETE_SRSP'
    SYS_OSAL_NV_LENGTH_SRSP = SYS_OSAL_NV_DELETE_SRSP
    SYS_ADC_READ_SRSP = 'SYS_ADC_READ_SRSP'
    SYS_GPIO_SRSP = 'SYS_GPIO_RSP'
    SYS_RANDOM_SRSP = 'SYS_RANDOM_SRSP'
    SYS_SET_TIME_SRSP = 'SYS_SET_TIME_SRSP'
    SYS_GET_TIME_SRSP = 'SYS_GET_TIME_SRSP'
    SYS_SET_TX_POWER_SRSP = 'SYS_SET_TX_POWER_SRSP'
    ZB_READ_CONFIGURATION_SRSP = 'ZB_READ_CONFIGURATION_SRSP'
    ZB_WRITE_CONFIGURATION_SRSP = 'ZB_WRITE_CONFIGURATION_SRSP'
    ZB_APP_REGISTER_REQUEST_SRSP = 'ZB_APP_REGISTER_REQUEST_SRSP'
    ZB_START_REQUEST_SRSP = 'ZB_START_REQUEST_SRSP'
    ZB_START_CONFIRM = 'ZB_START_CONFIRM'
    ZB_PERMIT_JOINING_REQUEST_SRSP = 'ZB_PERMIT_JOINING_REQUEST_SRSP'
    ZB_BIND_DEVICE_SRSP = 'ZB_BIND_DEVICE_SRSP'
    ZB_BIND_CONFIRM = 'ZB_BIND_CONFIRM'
    ZB_ALLOW_BIND_SRSP = 'ZB_ALLOW_BIND_SRSP'
    ZB_ALLOW_BIND_CONFIRM = 'ZB_ALLOW_BIND_CONFIRM'
    ZB_SEND_DATA_REQUEST_SRSP = 'ZB_SEND_DATA_REQUEST_SRSP'
    ZB_SEND_DATA_CONFIRM = 'ZB_SEND_DATA_CONFIRM'
    ZB_RECEIVE_DATA_INDICATION = 'ZB_RECEIVE_DATA_INDICATION'
    ZB_GET_DEVICE_INFO_SRSP = 'ZB_GET_DEVICE_INFO_SRSP'
    ZB_FIND_DEVICE_REQUEST_SRSP = 'ZB_FIND_DEVICE_REQUEST_SRSP'
    ZB_FIND_DEVICE_CONFIRM = 'ZB_FIND_DEVICE_CONFIRM'
    AF_REGISTER_SRSP = 'AF_REGISTER_SRSP'
    AF_DATA_REQUEST_SRSP = 'AF_DATA_REQUEST_SRSP'
    AF_DATA_REQUEST_EXT_SRSP = 'AF_DATA_REQUEST_EXT_SRSP'
    AF_DATA_REQUEST_SRC_RTG_SRSP = AF_DATA_REQUEST_EXT_SRSP
    AF_INTER_PAN_CTRL_SRSP = 'AF_INTER_PAN_CTRL_SRSP'
    AF_DATA_STORE_SRSP = 'AF_DATA_STORE_SRSP'
    AF_DATA_CONFIRM = 'AF_DATA_CONFIRM'
    AF_INCOMING_MSG = 'AF_INCOMING_MSG'
    AF_INCOMING_MSG_EXT = 'AF_INCOMING_MSG_EXT'
    AF_DATA_RETRIEVE_SRSP = 'AF_DATA_RETRIEVE_SRSP'
    AF_APSF_CONFIG_SET_SRSP = 'AF_APSF_CONFIG_SET_SRSP'
    ZDO_NWK_ADDR_REQ_SRSP = 'ZDO_NWK_ADDR_REQ_SRSP'
    ZDO_IEEE_ADDR_REQ_SRSP = 'ZDO_IEEE_ADDR_REQ_SRSP'
    ZDO_NODE_DESC_REQ_SRSP = 'ZDO_NODE_DESC_REQ_SRSP'
    ZDO_POWER_DESC_REQ_SRSP = 'ZDO_POWER_DESC_REQ_SRSP'
    ZDO_SIMPLE_DESC_REQ_SRSP = 'ZDO_SIMPLE_DESC_REQ_SRSP'
    ZDO_ACTIVE_EP_REQ_SRSP = 'ZDO_ACTIVE_EP_REQ_SRSP'
    ZDO_MATCH_DESC_REQ_SRSP = 'ZDO_MATCH_DESC_REQ_SRSP'
    ZDO_COMPLEX_DESC_REQ_SRSP = 'ZDO_COMPLEX_DESC_REQ_SRSP'
    ZDO_USER_DESC_REQ_SRSP = 'ZDO_USER_DESC_REQ_SRSP'
    ZDO_DEVICE_ANNCE_SRSP = 'ZDO_DEVICE_ANNCE_SRSP'
    ZDO_USER_DESC_SET_SRSP = 'ZDO_USER_DESC_SET_SRSP'
    ZDO_SERVER_DESC_REQ_SRSP = 'ZDO_SERVER_DESC_REQ_SRSP'
    ZDO_END_DEVICE_BIND_REQ_SRSP = 'ZDO_END_DEVICE_BIND_REQ_SRSP'
    ZDO_BIND_REQ_SRSP = 'ZDO_BIND_REQ_SRSP'
    ZDO_UNBIND_REQ_SRSP = 'ZDO_UNBIND_REQ_SRSP'
    ZDO_MGMT_NWK_DISC_REQ_SRSP = 'ZDO_MGMT_NWK_DISC_REQ_SRSP'
    ZDO_MGMT_LQI_REQ_SRSP = 'ZDO_MGMT_LQI_REQ_SRSP'
    ZDO_MGMT_RTG_REQ_SRSP = 'ZDO_MGMT_RTG_REQ_SRSP'
    ZDO_MGMT_BIND_REQ_SRSP = 'ZDO_MGMT_BIND_REQ_SRSP'
    ZDO_MGMT_LEAVE_REQ_SRSP = 'ZDO_MGMT_LEAVE_REQ_SRSP'
    ZDO_MGMT_DIRECT_JOIN_REQ_SRSP = 'ZDO_MGMT_DIRECT_JOIN_REQ_SRSP'
    ZDO_MGMT_PERMIT_JOIN_REQ_SRSP = 'ZDO_MGMT_PERMIT_JOIN_REQ_SRSP'
    ZDO_MGMT_NWK_UPDATE_REQ_SRSP = 'ZDO_MGMT_NWK_UPDATE_REQ_SRSP'
    ZDO_STARTUP_FROM_APP_SRSP = 'ZDO_STARTUP_FROM_APP_SRSP'
    ZDO_SET_LINK_KEY_SRSP = 'ZDO_SET_LINK_KEY_SRSP'
    ZDO_REMOVE_LINK_KEY_SRSP = 'ZDO_REMOVE_LINK_KEY_SRSP'
    ZDO_GET_LINK_KEY_SRSP = 'ZDO_GET_LINK_KEY_SRSP'
    ZDO_NWK_DISCOVERY_REQ_SRSP = 'ZDO_NWK_DISCOVERY_REQ_SRSP'
    ZDO_JOIN_REQ_SRSP = 'ZDO_JOIN_REQ_SRSP'
    ZDO_NWK_ADDR_RSP = 'ZDO_NWK_ADDR_RSP'
    ZDO_IEEE_ADDR_RSP = 'ZDO_IEEE_ADDR_RSP'
    ZDO_NODE_DESC_RSP = 'ZDO_NODE_DESC_RSP'
    ZDO_POWER_DESC_RSP = 'ZDO_POWER_DESC_RSP'
    ZDO_SIMPLE_DESC_RSP = 'ZDO_SIMPLE_DESC_RSP'
    ZDO_ACTIVE_EP_RSP = 'ZDO_ACTIVE_EP_RSP'
    ZDO_MATCH_DESC_RSP = 'ZDO_MATCH_DESC_RSP'
    ZDO_COMPLEX_DESC_RSP = 'ZDO_COMPLEX_DESC_RSP'
    ZDO_USER_DESC_RSP = 'ZDO_USER_DESC_RSP'
    ZDO_USER_DESC_CONF = 'ZDO_USER_DESC_CONF'
    ZDO_SERVER_DESC_RSP = 'ZDO_SERVER_DESC_RSP'
    ZDO_END_DEVICE_BIND_RSP = 'ZDO_END_DEVICE_BIND_RSP'
    ZDO_BIND_RSP = 'ZDO_BIND_RSP'
    ZDO_UNBIND_RSP = 'ZDO_UNBIND_RSP'
    ZDO_MGMT_NWK_DISC_RSP = 'ZDO_MGMT_NWK_DISC_RSP'
    ZDO_MGMT_LQI_RSP = 'ZDO_MGMT_LQI_RSP'
    ZDO_MGMT_RTG_RSP = 'ZDO_MGMT_RTG_RSP'
    ZDO_MGMT_BIND_RSP = 'ZDO_MGMT_BIND_RSP'
    ZDO_MGMT_LEAVE_RSP = 'ZDO_MGMT_LEAVE_RSP'
    ZDO_MGMT_DIRECT_JOIN_RSP = 'ZDO_MGMT_DIRECT_JOIN_RSP'
    ZDO_MGMT_PERMIT_JOIN_RSP = 'ZDO_MGMT_PERMIT_JOIN_RSP'
    ZDO_STATE_CHANGE_IND = 'ZDO_STATE_CHANGE_IND'
    ZDO_END_DEVICE_ANNCE_IND = 'ZDO_END_DEVICE_ANNCE_IND'
    ZDO_MATCH_DESC_RSP_SENT = 'ZDO_MATCH_DESC_RSP_SENT'
    ZDO_STATUS_ERROR_RSP = 'ZDO_STATUS_ERROR_RSP'
    ZDO_SRC_RTG_IND = 'ZDO_SRC_RTG_IND'
    ZDO_LEAVE_IND = 'ZDO_LEAVE_IND'
    ZDO_MSG_CB_REGISTER_SRSP = 'ZDO_MSG_CB_REGISTER_SRSP'
    ZDO_MSG_CB_REMOVE_SRSP = 'ZDO_MSG_CB_REMOVE_SRSP'
    ZDO_MSG_CB_INCOMING = 'ZDO_MSG_CB_INCOMING'
    UTIL_DATA_REQ_SRSP = 'UTIL_DATA_REQ_SRSP'
    UTIL_ADDRMGR_EXT_ADDR_LOOKUP_SRSP = 'UTIL_ADDRMGR_EXT_ADDR_LOOKUP_SRSP'
    UTIL_ADDRMGR_NWK_ADDR_LOOKUP_SRSP = 'UTIL_ADDRMGR_NWK_ADDR_LOOKUP_SRSP'
    UTIL_APSME_LINK_KEY_DATA_GET_SRSP = 'UTIL_APSME_LINK_KEY_DATA_GET_SRSP'
    UTIL_APSME_LINK_KEY_NV_ID_GET_SRSP = 'UTIL_APSME_LINK_KEY_NV_ID_GET_SRSP'
    UTIL_APSME_REQUEST_KEY_CMD_SRSP = 'UTIL_APSME_REQUEST_KEY_CMD_SRSP'
    UTIL_ASSOC_COUNT_SRSP = 'UTIL_ASSOC_COUNT_SRSP'
    UTIL_ASSOC_FIND_DEVICE_SRSP = 'UTIL_ASSOC_FIND_DEVICE_SRSP'
    UTIL_ZCL_KEY_EST_INIT_EST_SRSP = 'UTIL_ZCL_KEY_EST_INIT_EST_SRSP'
    UTIL_ZCL_KEY_EST_SIGN_SRSP = 'UTIL_ZCL_KEY_EST_SIGN_SRSP'
    UTIL_TEST_LOOPBACK_SRSP = 'UTIL_TEST_LOOPBACK_SRSP' 
    
    #APS Expanded 
    APS_ADD_GROUP_SRSP = 'APS_ADD_GROUP_SRSP'
    APS_REMOVE_GROUP_SRSP = 'APS_REMOVE_GROUP_SRSP'
    APS_REMOVE_ALL_GROUP_SRSP = 'APS_REMOVE_ALL_GROUP_SRSP'
    APS_FIND_GROUP_SRSP = 'APS_FIND_GROUP_SRSP'
    APS_FIND_ALL_GROUPS_FOR_EP_SRSP = 'APS_FIND_ALL_GROUPS_FOR_EP_SRSP'
    APS_COUNT_ALL_GROUPS_SRSP = 'APS_COUNT_ALL_GROUPS_SRSP'
        
                
class ZpiCommands(object):
    """
        Implemented according to CC2530-ZNP interface specification, Z-stack 2.5.1a
        Basically, ZNP frame is very similar to XBee API frame
        XBee API format    : SOF:1, LEN:2, CMD_ID:1, CMD_DATA:n, CHKSUM:1
        CC2530-ZNP format  : SOF:1, LEN:1, CMD0:1, CMD1:1, DATA:n, FCS:1
    """
    znp_commands = {
        #SYS interface
        ZpiCommand.SYS_RESET_REQ:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x41'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x00'},
            {'name': 'type',        'len': 1,   'default': None},
            ],
        ZpiCommand.SYS_VERSION:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x21'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x02'},       
            ],
        ZpiCommand.SYS_OSAL_NV_READ:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x21'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x08'},
            {'name': 'id',          'len': 2,   'default': None},
            {'name': 'offset',      'len': 1,   'default': None},                 
            ],     
        ZpiCommand.SYS_OSAL_NV_WRITE:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x21'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x09'},    
            {'name': 'id',          'len': 2,   'default': None},
            {'name': 'offset',      'len': 1,   'default': None},    
            {'name': 'len',         'len': 1,   'default': None},
            {'name': 'value',       'len': None,'default': None},
            ],
        ZpiCommand.SYS_OSAL_NV_ITEM_INIT:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x21'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x07'},    
            {'name': 'id',          'len': 2,   'default': None},
            {'name': 'item_len',    'len': 2,   'default': None},    
            {'name': 'init_len',    'len': 1,   'default': None},
            {'name': 'init_data',   'len': None,'default': None},
            ],   
        ZpiCommand.SYS_OSAL_NV_DELETE:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x21'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x12'},    
            {'name': 'id',          'len': 2,   'default': None},
            {'name': 'item_len',    'len': 2,   'default': None},    
            ],  
        ZpiCommand.SYS_OSAL_NV_LENGTH:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x21'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x13'},    
            {'name': 'id',          'len': 2,   'default': None},
            ],         
        ZpiCommand.SYS_ADC_READ:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x21'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x0d'},
            {'name': 'channel',     'len': 1,   'default': None},
            {'name': 'resolution',  'len': 1,   'default': None},   
            ],
        ZpiCommand.SYS_GPIO:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x21'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x0e'},   
            {'name': 'operation',   'len': 1,   'default': None},
            {'name': 'value',       'len': 1,   'default': None}, 
            ],
        ZpiCommand.SYS_RANDOM:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x21'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x0c'},       
            ],
        ZpiCommand.SYS_SET_TIME:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x21'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x10'},    
            {'name': 'utc_time',    'len': 4,   'default': None},
            {'name': 'hour',        'len': 1,   'default': None},    
            {'name': 'minute',      'len': 1,   'default': None},
            {'name': 'second',      'len': 1,   'default': None},
            {'name': 'month',       'len': 1,   'default': None},    
            {'name': 'day',         'len': 1,   'default': None},
            {'name': 'year',        'len': 2,   'default': None},
            ],   
        ZpiCommand.SYS_GET_TIME:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x21'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x11'},    
            ],     
        ZpiCommand.SYS_SET_TX_POWER:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x21'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x14'},    
            {'name': 'tx_power',    'len': 1,   'default': None},
            ],           
        #Configuration interface
        ZpiCommand.ZB_READ_CONFIGURATION:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x26'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x04'}, 
            {'name': 'config_id',  'len': 1,   'default': None},
            ],      
        ZpiCommand.ZB_WRITE_CONFIGURATION:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x26'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x05'}, 
            {'name': 'config_id',  'len': 1,   'default': None},
            {'name': 'len',         'len': 1,   'default': None},
            {'name': 'value',       'len': None,'default': None},
            ],        
                    
        #Simple API  
        ZpiCommand.ZB_APP_REGISTER_REQUEST:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x26'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x0a'}, 
            {'name': 'endpoint',    'len': 1,   'default': None},  
            {'name': 'profile_id',  'len': 2,   'default': None},  
            {'name': 'device_id',   'len': 2,   'default': None},  
            {'name': 'device_ver',  'len': 1,   'default': None},   
            {'name': 'unused',      'len': 1,   'default': b'\x00'},
            {'name': 'in_cmd_num',  'len': 1,   'default': None},     
            {'name': 'in_cmd_list',     'len': ('in_cmd_num', '2*x'),   'default': None},  
            {'name': 'out_cmd_num', 'len': 1,   'default': None}, 
            {'name': 'out_cmd_list',    'len': ('out_cmd_num', '2*x'),   'default': None},         
            ],   
        ZpiCommand.ZB_START_REQUEST:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x26'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x00'},                                
            ],      
        ZpiCommand.ZB_PERMIT_JOINING_REQUEST:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x26'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x08'}, 
            {'name': 'dst_addr',    'len': 2,   'default': None},  
            {'name': 'timeout',     'len': 1,   'default': None},                                
            ], 
        ZpiCommand.ZB_BIND_DEVICE:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x26'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x01'}, 
            {'name': 'create',      'len': 1,   'default': None},  
            {'name': 'cmd_id',      'len': 2,   'default': None},    
            {'name': 'dst_addr_long',     'len': 8,   'default': None},                          
            ], 
        ZpiCommand.ZB_ALLOW_BIND:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x26'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x02'},  
            {'name': 'timeout',     'len': 1,   'default': None},                                
            ],       
        ZpiCommand.ZB_SEND_DATA_REQUEST:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x26'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x03'},  
            {'name': 'dst_addr_short',  'len': 2,   'default': None},  
            {'name': 'cmd_id',      'len': 2,   'default': None},  
            {'name': 'handle',      'len': 1,   'default': '\x00'},     
            {'name': 'ack',         'len': 1,   'default': '\x01'},   
            {'name': 'radius',      'len': 1,   'default': '\x00'},   
            {'name': 'len',         'len': 1,   'default': None}, 
            {'name': 'data',        'len': None,'default': None},               
            ],   
        ZpiCommand.ZB_GET_DEVICE_INFO:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x26'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x06'},  
            {'name': 'param',       'len': 1,   'default': None},                                
            ],  
        ZpiCommand.ZB_FIND_DEVICE_REQUEST:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x26'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x07'},  
            {'name': 'search_key',  'len': 8,   'default': None},                                
            ],  
                    
        #AF interface
        ZpiCommand.AF_REGISTER:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x24'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x00'},  
            {'name': 'endpoint',    'len': 1,   'default': None},   
            {'name': 'profile_id',  'len': 2,   'default': None},  
            {'name': 'device_id',   'len': 2,   'default': None},  
            {'name': 'device_ver',  'len': 1,   'default': None},  
            {'name': 'latency_req', 'len': 1,   'default': None},  
            {'name': 'in_cluster_num','len': 1,   'default': None},
            {'name': 'in_cluster_list',  'len': ('in_cluster_num', '2*x'),   'default': None},   
            {'name': 'out_cluster_num','len': 1,   'default': None},  
            {'name': 'out_cluster_list', 'len': ('out_cluster_num', '2*x'),   'default': None},                          
            ],  
        ZpiCommand.AF_DATA_REQUEST:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x24'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x01'},  
            {'name': 'dst_addr',    'len': 2,   'default': None},  
            {'name': 'dst_ep',      'len': 1,   'default': None},  
            {'name': 'src_ep',      'len': 1,   'default': None},     
            {'name': 'cluster_id',  'len': 2,   'default': None},   
            {'name': 'trans_id',    'len': 1,   'default': None},   
            {'name': 'options',     'len': 1,   'default': None}, 
            {'name': 'radius',      'len': 1,   'default': None},   
            {'name': 'len',         'len': 1,   'default': None}, 
            {'name': 'data',        'len': None,'default': None}, 
            ],    
                     
        ZpiCommand.AF_DATA_REQUEST_EXT:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x24'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x02'},  
            {'name': 'dst_addr_mode','len': 1,   'default': None},  
            {'name': 'dst_addr',    'len': 8,   'default': None},  
            {'name': 'dst_ep',      'len': 1,   'default': None},  
            {'name': 'dst_pan_id',  'len': 2,   'default': None},  
            {'name': 'src_ep',      'len': 1,   'default': None},     
            {'name': 'cluster_id',  'len': 2,   'default': None},   
            {'name': 'trans_id',    'len': 1,   'default': None},   
            {'name': 'options',     'len': 1,   'default': None}, 
            {'name': 'radius',      'len': 1,   'default': None},   
            {'name': 'len',         'len': 2,   'default': None},
            {'name': 'data',        'len': None,'default': None}, 
            ],   
                    
        ZpiCommand.AF_DATA_REQUEST_SRC_RTG:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x24'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x02'},
            {'name': 'dst_addr',    'len': 2,   'default': None},
            {'name': 'dst_ep',      'len': 1,   'default': None},
            {'name': 'src_ep',      'len': 1,   'default': None},
            {'name': 'cluster_id',  'len': 2,   'default': None},
            {'name': 'trans_id',    'len': 1,   'default': None},
            {'name': 'options',     'len': 1,   'default': None},
            {'name': 'radius',      'len': 1,   'default': None},
            {'name': 'relay_cnt',   'len': 1,   'default': None},
            {'name': 'relay_list',  'len': ('relay_cnt', '2*x'),  'default': None},
            {'name': 'len',         'len': 1,   'default': None},  
            {'name': 'data',        'len': None,'default': None}, 
            ], 
                    
        ZpiCommand.AF_INTER_PAN_CTRL:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x24'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x10'},  
            {'name': 'command',     'len': 1,   'default': None},  
            {'name': 'data',        'len': None,'default': None}, 
            ],   
                    
        ZpiCommand.AF_DATA_STORE:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x24'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x11'},  
            {'name': 'index',       'len': 2,   'default': None},  
            {'name': 'len',         'len': 1,   'default': None}, 
            {'name': 'data',        'len': None,'default': None},
            ],  
                    
        ZpiCommand.AF_DATA_RETRIEVE:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x24'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x12'},  
            {'name': 'time_stamp',  'len': 4,   'default': None},
            {'name': 'index',       'len': 2,   'default': None},  
            {'name': 'len',         'len': 1,   'default': None}, 
            ],  
        
        ZpiCommand.AF_APSF_CONFIG_SET:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x24'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x13'},  
            {'name': 'endpoint',    'len': 1,   'default': None},
            {'name': 'frame_delay', 'len': 1,   'default': None},  
            {'name': 'window_size', 'len': 1,   'default': None}, 
            ],
                    
                    
        #ZDO interface
        ZpiCommand.ZDO_NWK_ADDR_REQ:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x25'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x00'},  
            {'name': 'ieee_addr',   'len': 8,   'default': None},
            {'name': 'req_type',    'len': 1,   'default': b'\x00'},  
            {'name': 'start_index', 'len': 1,   'default': b'\x00'}, 
            ],
        ZpiCommand.ZDO_IEEE_ADDR_REQ:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x25'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x01'},  
            {'name': 'nwk_addr',   'len': 2,   'default': None},
            {'name': 'req_type',    'len': 1,   'default': b'\x00'},  
            {'name': 'start_index', 'len': 1,   'default': b'\x00'}, 
            ],
        ZpiCommand.ZDO_NODE_DESC_REQ:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x25'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x02'},  
            {'name': 'dst_addr',    'len': 2,   'default': None},
            {'name': 'nwk_addr_of_interest',    'len': 2,   'default': None},  
            ],     
        ZpiCommand.ZDO_POWER_DESC_REQ:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x25'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x03'},  
            {'name': 'dst_addr',    'len': 2,   'default': None},
            {'name': 'nwk_addr_of_interest',    'len': 2,   'default': None},  
            ], 
        ZpiCommand.ZDO_SIMPLE_DESC_REQ:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x25'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x04'},  
            {'name': 'dst_addr',    'len': 2,   'default': None},
            {'name': 'nwk_addr_of_interest',    'len': 2,   'default': None},  
            {'name': 'endpoint',    'len': 1,   'default': None},
            ],  
        ZpiCommand.ZDO_ACTIVE_EP_REQ:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x25'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x05'},  
            {'name': 'dst_addr',    'len': 2,   'default': None},
            {'name': 'nwk_addr_of_interest',    'len': 2,   'default': None},  
            ],          
        ZpiCommand.ZDO_MATCH_DESC_REQ:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x25'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x06'},  
            {'name': 'dst_addr',    'len': 2,   'default': None},
            {'name': 'nwk_addr_of_interest',    'len': 2,   'default': None}, 
            {'name': 'profile_id',  'len': 2,   'default': None},
            {'name': 'in_clusters_num',    'len': 1,   'default': None}, 
            {'name': 'in_cluster_list', 'len': ('in_clusters_num', '2*x'),   'default': None},
            {'name': 'out_clusters_num',    'len': 1,   'default': None}, 
            {'name': 'out_cluster_list','len': ('out_clusters_num', '2*x'),   'default': None},
            ],  
        ZpiCommand.ZDO_COMPLEX_DESC_REQ:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x25'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x07'},  
            {'name': 'dst_addr',    'len': 2,   'default': None},
            {'name': 'nwk_addr_of_interest',    'len': 2,   'default': None},  
            ],     
        ZpiCommand.ZDO_USER_DESC_REQ:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x25'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x08'},  
            {'name': 'dst_addr',    'len': 2,   'default': None},
            {'name': 'nwk_addr_of_interest',    'len': 2,   'default': None},  
            ],   
        ZpiCommand.ZDO_DEVICE_ANNCE:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x25'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x0a'},  
            {'name': 'nwk_addr',    'len': 2,   'default': None},
            {'name': 'ieee_addr',   'len': 8,   'default': None},  
            {'name': 'capabilities','len': 1,   'default': None},  
            ],  
        ZpiCommand.ZDO_USER_DESC_SET:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x25'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x0b'},  
            {'name': 'dst_addr',    'len': 2,   'default': None},
            {'name': 'nwk_addr_of_interest',    'len': 2,   'default': None}, 
            {'name': 'len',         'len': 1,   'default': None},
            {'name': 'user_descriptor',   'len': None, 'default': None}, 
            ],  
        ZpiCommand.ZDO_SERVER_DESC_REQ:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x25'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x0c'},  
            {'name': 'server_mask', 'len': 2,   'default': None}, 
            ],   
        ZpiCommand.ZDO_END_DEVICE_BIND_REQ:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x25'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x20'},  
            {'name': 'dst_addr',    'len': 2,   'default': None},
            {'name': 'local_coord', 'len': 2,   'default': b'\x00\x00'},
            {'name': 'ieee',        'len': 8,    'default': b'\x00\x00\x00\x00\x00\x00\x00\x00'},
            {'name': 'endpoint',    'len': 1,   'default': None},
            {'name': 'profile_id', 'len': 2,   'default': None},
            {'name': 'in_cluster_num',    'len': 1,   'default': None},
            {'name': 'in_cluster_list', 'len': ('in_cluster_num', '2*x'),   'default': None},
            {'name': 'out_cluster_num',    'len': 1,   'default': None},
            {'name': 'out_cluster_list', 'len': ('out_cluster_num', '2*x'),   'default': None},
            ], 
        ZpiCommand.ZDO_BIND_REQ:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x25'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x21'},  
            {'name': 'dst_addr',    'len': 2,   'default': None},
            {'name': 'src_addr',    'len': 8,   'default': None},  
            {'name': 'src_ep',      'len': 1,   'default': None},  
            {'name': 'cluster_id',  'len': 2,   'default': None},  
            {'name': 'bind_addr_mode',    'len': 1,   'default': None},  
            {'name': 'bind_addr',    'len': 8,   'default': None},  
            {'name': 'bind_ep',      'len': 1,   'default': None},  
            ], 
        ZpiCommand.ZDO_UNBIND_REQ:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x25'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x22'},  
            {'name': 'dst_addr',    'len': 2,   'default': None},
            {'name': 'src_addr',    'len': 8,   'default': None},
            {'name': 'src_ep',      'len': 1,   'default': None},
            {'name': 'cluster_id',  'len': 2,   'default': None},  
            {'name': 'bind_addr_mode',    'len': 1,   'default': None},
            {'name': 'bind_addr',    'len': 8,   'default': None},
            {'name': 'bind_ep',      'len': 1,   'default': None},  
            ], 
        ZpiCommand.ZDO_MGMT_NWK_DISC_REQ:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x25'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x30'},  
            {'name': 'dst_addr',    'len': 2,   'default': None},
            {'name': 'scan_channels',   'len': 4,   'default': None},  
            {'name': 'scan_duration',   'len': 1,   'default': None},  
            {'name': 'start_index',     'len': 1,   'default': None},  
            ], 
        ZpiCommand.ZDO_MGMT_LQI_REQ:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x25'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x31'},  
            {'name': 'dst_addr',    'len': 2,   'default': None},
            {'name': 'start_index', 'len': 2,   'default': None},  
            ],
        ZpiCommand.ZDO_MGMT_RTG_REQ:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x25'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x32'},  
            {'name': 'dst_addr',    'len': 2,   'default': None},
            {'name': 'start_index', 'len': 1,   'default': None},  
            ],     
        ZpiCommand.ZDO_MGMT_BIND_REQ:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x25'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x33'},  
            {'name': 'dst_addr',    'len': 2,   'default': None},
            {'name': 'start_index', 'len': 1,   'default': None},  
            ],    
        ZpiCommand.ZDO_MGMT_LEAVE_REQ:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x25'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x34'},  
            {'name': 'dst_addr',    'len': 2,   'default': None},
            {'name': 'device_addr', 'len': 8,   'default': None},  
            {'name': 'remove_children_rejoin', 'len': 1,   'default': None},  
            ],  
        ZpiCommand.ZDO_MGMT_DIRECT_JOIN_REQ:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x25'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x35'},  
            {'name': 'dst_addr',    'len': 2,   'default': None},
            {'name': 'device_addr', 'len': 8,   'default': None},  
            {'name': 'cap_info',    'len': 1,   'default': None}, 
            ],    
        ZpiCommand.ZDO_MGMT_PERMIT_JOIN_REQ:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x25'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x36'},  
            {'name': 'addr_mode',   'len': 1,   'default': None},       #update for Z-stack 2.6.1
            {'name': 'dst_addr',    'len': 2,   'default': None},
            {'name': 'duration',    'len': 1,   'default': None},  
            {'name': 'tc_significance',    'len': 1,   'default': None}, 
            ],     
        ZpiCommand.ZDO_MGMT_NWK_UPDATE_REQ:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x25'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x37'},  
            {'name': 'dst_addr',    'len': 2,   'default': None},
            {'name': 'dst_addr_mode',   'len': 1,   'default': None}, 
            {'name': 'channel_mask',    'len': 4,   'default': None},  
            {'name': 'scan_duration',   'len': 1,   'default': None},  
            {'name': 'scan_count',   'len': 1,   'default': None},  
            {'name': 'nwk_manager_addr', 'len': 2,   'default': None},  
            ],   
        ZpiCommand.ZDO_STARTUP_FROM_APP:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x25'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x40'},  
            {'name': 'start_delay', 'len': 2,   'default': None},
            ],   
        ZpiCommand.ZDO_AUTO_FIND_DESTINATION:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x45'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x41'},  
            {'name': 'endpoint',    'len': 1,   'default': None},
            ],  
        ZpiCommand.ZDO_SET_LINK_KEY:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x25'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x23'},  
            {'name': 'nwk_addr',    'len': 2,   'default': None},
            {'name': 'ieee_addr',   'len': 8,   'default': None}, 
            {'name': 'link_key_data',   'len': 16,   'default': None}, 
            ],  
        ZpiCommand.ZDO_REMOVE_LINK_KEY:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x25'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x24'},  
            {'name': 'ieee_addr',   'len': 8,   'default': None},  
            ],     
        ZpiCommand.ZDO_GET_LINK_KEY:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x25'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x25'},  
            {'name': 'ieee_addr',   'len': 8,   'default': None},  
            ],   
        ZpiCommand.ZDO_NWK_DISCOVERY_REQ:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x25'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x26'},  
            {'name': 'scan_channels',    'len': 4,   'default': None},
            {'name': 'scan_duration',    'len': 1,   'default': None},  
            ],   
        ZpiCommand.ZDO_JOIN_REQ:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x25'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x27'},  
            {'name': 'logical_chnnel',  'len': 1,   'default': None},
            {'name': 'pan_id',          'len': 2,   'default': None},  
            {'name': 'pan_id_ext',      'len': 8,   'default': None}, 
            {'name': 'chosen_parent',   'len': 2,   'default': None}, 
            {'name': 'parent_depth',    'len': 1,   'default': None}, 
            {'name': 'stack_profile',   'len': 1,   'default': None}, 
            ],  
        ZpiCommand.ZDO_MSG_CB_REGISTER:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x25'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x3e'},  
            {'name': 'cluster_id',  'len': 2,   'default': None}, 
            ],   
        ZpiCommand.ZDO_MSG_CB_REMOVE_REQ:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x25'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x3f'},  
            {'name': 'cluster_id',  'len': 2,   'default': None},  
            ],
                                                           
        #Util interface       
        ZpiCommand.UTIL_DATA_REQ:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x27'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x11'},  
            {'name': 'security_use','len': 1,   'default': b'\x00'},  
            ],        
        ZpiCommand.UTIL_ADDRMGR_EXT_ADDR_LOOKUP:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x27'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x40'},  
            {'name': 'ext_addr',    'len': 8,   'default': None},  
            ],   
        ZpiCommand.UTIL_ADDRMGR_NWK_ADDR_LOOKUP:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x27'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x41'},  
            {'name': 'nwk_addr',    'len': 2,   'default': None},  
            ],  
        ZpiCommand.UTIL_APSME_LINK_KEY_DATA_GET:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x27'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x44'},  
            {'name': 'ext_addr',    'len': 8,   'default': None},  
            ], 
        ZpiCommand.UTIL_APSME_LINK_KEY_NV_ID_GET:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x27'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x45'},  
            {'name': 'ext_addr',    'len': 8,   'default': None},  
            ],       
        ZpiCommand.UTIL_APSME_REQUEST_KEY_CMD:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x27'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x44'},  
            {'name': 'partner_addr','len': 8,   'default': None},  
            ],  
        ZpiCommand.UTIL_ASSOC_COUNT:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x27'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x48'},  
            {'name': 'start_relation',  'len': 1,   'default': None},  
            {'name': 'end_relation',    'len': 1,   'default': None},       
            ],    
        ZpiCommand.UTIL_ASSOC_FIND_DEVICE:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x27'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x49'},  
            {'name': 'number',      'len': 1,   'default': None},         
            ],          
        ZpiCommand.UTIL_ZCL_KEY_EST_INIT_EST:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x27'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x80'},  
            {'name': 'task_id',     'len': 1,   'default': None},  
            {'name': 'seq_num',     'len': 1,   'default': None},   
            {'name': 'endpoint',    'len': 1,   'default': None},    
            {'name': 'addr_mode',   'len': 1,   'default': None},    
            {'name': 'addr',        'len': 8,   'default': None},    
            ],  
        ZpiCommand.UTIL_ZCL_KEY_EST_SIGN:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x27'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x81'},  
            {'name': 'input_len',   'len': 1,   'default': None},  
            {'name': 'input',       'len': 1,   'default': None},       
            ],   
        ZpiCommand.UTIL_ZCL_KEY_EST_IND:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x47'},
            {'name': 'cmd1',        'len': 1,   'default': b'\xe1'},  
            {'name': 'task_id',     'len': 1,   'default': None},  
            {'name': 'event',       'len': 1,   'default': None},   
            {'name': 'status',      'len': 1,   'default': None},    
            {'name': 'wait_time',   'len': 1,   'ININDdefault': None},    
            {'name': 'suite',       'len': 2,   'default': None},    
            ],     
        ZpiCommand.UTIL_TEST_LOOPBACK:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x27'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x10'},  
            {'name': 'test_data',   'len': 1,   'default': None},      
            ],       
                    
        #APS interface (expanded for ZCL group/scene support in application side
        ZpiCommand.APS_ADD_GROUP:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x2f'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x00'},  
            {'name': 'endpoint',    'len': 1,   'default': None},   
            {'name': 'group_id',    'len': 2,   'default': None},
            {'name': 'group_name',  'len': 16,  'default': None},   
            ],      
                    
        ZpiCommand.APS_REMOVE_GROUP:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x2f'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x01'},  
            {'name': 'endpoint',    'len': 1,   'default': None},   
            {'name': 'group_id',    'len': 2,   'default': None},  
            ],     
                    
        ZpiCommand.APS_REMOVE_ALL_GROUP:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x2f'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x02'},  
            {'name': 'endpoint',    'len': 1,   'default': None},     
            ],   
                    
        ZpiCommand.APS_FIND_GROUP:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x2f'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x03'},  
            {'name': 'endpoint',    'len': 1,   'default': None},   
            {'name': 'group_id',    'len': 2,   'default': None},  
            ],   
                    
        ZpiCommand.APS_FIND_ALL_GROUPS_FOR_EP:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x2f'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x04'},  
            {'name': 'endpoint',    'len': 1,   'default': None},   
            ],                                                   
                    
        ZpiCommand.APS_COUNT_ALL_GROUPS:[
            {'name': 'cmd0',        'len': 1,   'default': b'\x2f'},
            {'name': 'cmd1',        'len': 1,   'default': b'\x05'},   
            ],                                         
        }
    
    #---------------------------------------------------------------------------
    #ZNP response frames 
    #---------------------------------------------------------------------------
    znp_responses = {
        #SYS interface
        b'\x41\x80':{             
            'name': ZpiCommand.SYS_RESET_IND,
            'structure':[
                {'name': 'reason',          'len': 1},
                {'name': 'transport_rev',   'len': 1},
                {'name': 'product_id',      'len': 1},
                {'name': 'major_rel',       'len': 1},
                {'name': 'minor_rel',       'len': 1},
                {'name': 'hw_rev',          'len': 1}
                ],
            },
        b'\x61\x02':{
            'name': ZpiCommand.SYS_VERSION_SRSP,
            'structure':[
                {'name': 'transport_rev',   'len': 1},
                {'name': 'product_id',      'len': 1},
                {'name': 'major_rel',       'len': 1},
                {'name': 'minor_rel',       'len': 1},
                {'name': 'maint_rel',       'len': 1}
                ],
            },
        b'\x61\x08':{ 
            'name': ZpiCommand.SYS_OSAL_NV_READ_SRSP,
            'structure':[
                {'name': 'status',              'len': 1},
                {'name': 'len',                 'len': 1},
                {'name': 'value',               'len': None}
                ],
            },  
        b'\x61\x09':{ 
            'name': ZpiCommand.SYS_OSAL_NV_WRITE_SRSP,
            'structure':[
                {'name': 'status',              'len': 1},
                ],
            },
        b'\x61\x07':{ 
            'name': ZpiCommand.SYS_OSAL_NV_ITEM_INIT_SRSP,
            'structure':[
                {'name': 'status',              'len': 1},
                ],
            },     
        b'\x61\x12':{ 
            'name': ZpiCommand.SYS_OSAL_NV_DELETE_SRSP,  #same as SYS_OSAL_NV_LENGTH_SRSP
            'structure':[
                {'name': 'status',              'len': 1},
                ],
            },   
#        b'\x61\x12':{ 
#            'name': ZpiCommand.SYS_OSAL_NV_LENGTH_SRSP,#same as SYS_OSAL_NV_DELETE_SRSP
#            'structure':[
#                {'name': 'status',              'len': 1},
#                ],
#            },    
        b'\x61\x0d':{ 
            'name': ZpiCommand.SYS_ADC_READ_SRSP,
            'structure':[
                {'name': 'value',              'len': 2},
                ],
            },  
        b'\x61\x0e':{ 
            'name': ZpiCommand.SYS_GPIO_SRSP,
            'structure':[
                {'name': 'value',              'len': 1},
                ],
            },      
        b'\x61\x0c':{ 
            'name': ZpiCommand.SYS_RANDOM_SRSP,
            'structure':[
                {'name': 'value',              'len': 2},
                ],
            },         
        b'\x61\x10':{ 
            'name': ZpiCommand.SYS_SET_TIME_SRSP,
            'structure':[
                {'name': 'status',              'len': 1},
                ],
            },  
        b'\x61\x11':{ 
            'name': ZpiCommand.SYS_GET_TIME_SRSP,
            'structure':[
                {'name': 'utc_time',            'len': 1},
                {'name': 'hour',                'len': 1},
                {'name': 'minute',              'len': 1},
                {'name': 'second',              'len': 1},
                {'name': 'month',               'len': 1},
                {'name': 'day',                 'len': 1},
                {'name': 'year',                'len': 1},
                ],
            }, 
        b'\x61\x14':{ 
            'name': ZpiCommand.SYS_SET_TX_POWER_SRSP,
            'structure':[
                {'name': 'tx_power',            'len': 1},
                ],
            },        
                          
        #Configuration interface 
        b'\x66\x04':{ 
            'name': ZpiCommand.ZB_READ_CONFIGURATION_SRSP,
            'structure':[
                {'name': 'status',              'len': 1},
                {'name': 'config_id',           'len': 1},
                {'name': 'len',                 'len': 1},
                {'name': 'value',               'len': None},
                ],
            },  
        b'\x66\x05':{ 
            'name': ZpiCommand.ZB_WRITE_CONFIGURATION_SRSP,
            'structure':[
                {'name': 'status',              'len': 1},
                ],
            },  
                     
        #Simple API   
        b'\x66\x0a':{ 
            'name': ZpiCommand.ZB_APP_REGISTER_REQUEST_SRSP,
            'structure':[
                {'name': 'status',              'len': 1},
                ],
            },         
        b'\x66\x00':{ 
            'name': ZpiCommand.ZB_START_REQUEST_SRSP,
            'structure':[
                ],
            },        
        b'\x46\x80':{ 
            'name': ZpiCommand.ZB_START_CONFIRM,
            'structure':[
                {'name': 'status',              'len': 1},
                ],
            },        
        b'\x66\x08':{ 
            'name': ZpiCommand.ZB_PERMIT_JOINING_REQUEST_SRSP,
            'structure':[
                {'name': 'status',              'len': 1},
                ],
            },
        b'\x66\x01':{ 
            'name': ZpiCommand.ZB_BIND_DEVICE_SRSP,
            'structure':[
                ],
            },  
        b'\x46\x81':{ 
            'name': ZpiCommand.ZB_BIND_CONFIRM,
            'structure':[
                {'name': 'cmd_id',              'len': 2},
                {'name': 'status',              'len': 1},
                ],
            },    
        b'\x66\x02':{ 
            'name': ZpiCommand.ZB_ALLOW_BIND_SRSP,
            'structure':[
                ],
            },     
        b'\x46\x82':{ 
            'name': ZpiCommand.ZB_ALLOW_BIND_CONFIRM,
            'structure':[
                {'name': 'source',              'len': 2},
                #note: the byte below is not listed in spec but returned by ZNP 
                {'name': 'unused',              'len': 1},
                ],
            },          
        b'\x66\x03':{ 
            'name': ZpiCommand.ZB_SEND_DATA_REQUEST_SRSP,
            'structure':[
                ],
            },      
        b'\x46\x83':{ 
            'name': ZpiCommand.ZB_SEND_DATA_CONFIRM,
            'structure':[
                {'name': 'handle',              'len': 1},
                {'name': 'status',              'len': 1},
                ],
            },         
        b'\x46\x87':{ 
            'name': ZpiCommand.ZB_RECEIVE_DATA_INDICATION,
            'structure':[
                {'name': 'src_addr',            'len': 2},
                {'name': 'cmd',                 'len': 2},
                {'name': 'len',                 'len': 2},
                {'name': 'data',                'len': None},
                ],
            },     
        b'\x66\x06':{ 
            'name': ZpiCommand.ZB_GET_DEVICE_INFO_SRSP,
            'structure':[
                {'name': 'param',              'len': 1},
                {'name': 'value',              'len': 8},
                ],
            },     
        b'\x66\x07':{ 
            'name': ZpiCommand.ZB_FIND_DEVICE_REQUEST_SRSP,
            'structure':[
                ],
            },        
        b'\x46\x85':{ 
            'name': ZpiCommand.ZB_FIND_DEVICE_CONFIRM,
            'structure':[
                {'name': 'search_type',         'len': 1},
                {'name': 'search_key',          'len': 2},
                {'name': 'result',              'len': 8},
                ]
            }, 
  
        #AF interface
        b'\x64\x00':{ 
            'name': ZpiCommand.AF_REGISTER_SRSP,
            'structure':[
                {'name': 'status',              'len': 1},
                ]
            },      
        b'\x64\x01':{ 
            'name': ZpiCommand.AF_DATA_REQUEST_SRSP,
            'structure':[
                {'name': 'status',              'len': 1},
                ]
            },    
        b'\x64\x02':{ 
            'name': ZpiCommand.AF_DATA_REQUEST_EXT_SRSP,  #shared with AF_DATA_REQ_SRC_RTG
            'structure':[
                {'name': 'status',              'len': 1},
                ]
            },    
        b'\x64\x10':{ 
            'name': ZpiCommand.AF_INTER_PAN_CTRL_SRSP,
            'structure':[
                {'name': 'status',              'len': 1},
                ]
            },  
        b'\x64\x11':{ 
            'name': ZpiCommand.AF_DATA_STORE_SRSP,
            'structure':[
                {'name': 'status',              'len': 1},
                ]
            }, 
        b'\x44\x80':{ 
            'name': ZpiCommand.AF_DATA_CONFIRM,
            'structure':[
                {'name': 'status',              'len': 1},
                {'name': 'endpoint',            'len': 1},
                {'name': 'trans_id',            'len': 1},               
                ]
            },       
        b'\x44\x81':{ 
            'name': ZpiCommand.AF_INCOMING_MSG,
            'structure':[
                {'name': 'group_id',            'len': 2},
                {'name': 'cluster_id',          'len': 2},
                {'name': 'src_addr',            'len': 2},       
                {'name': 'src_ep',              'len': 1},
                {'name': 'dst_ep',              'len': 1},
                {'name': 'was_broadcast',       'len': 1},   
                {'name': 'lqi',                 'len': 1},
                {'name': 'security_use',        'len': 1},
                {'name': 'time_stamp',          'len': 4},   
                {'name': 'trans_seq',           'len': 1},  
                {'name': 'len',                 'len': 1},  
                {'name': 'data',                'len': None},  
                ]
            },  
        b'\x44\x82':{ 
            'name': ZpiCommand.AF_INCOMING_MSG_EXT,
            'structure':[
                {'name': 'group_id',            'len': 2},
                {'name': 'cluster_id',          'len': 2},
                {'name': 'src_addr_mode',       'len': 1},
                {'name': 'src_addr',            'len': 8},       
                {'name': 'src_ep',              'len': 1},
                {'name': 'src_pan_id',          'len': 2},
                {'name': 'dst_ep',              'len': 1},
                {'name': 'was_broadcast',       'len': 1},   
                {'name': 'lqi',                 'len': 1},
                {'name': 'security_use',        'len': 1},
                {'name': 'time_stamp',          'len': 4},   
                {'name': 'trans_seq',           'len': 1},  
                {'name': 'len',                 'len': 2},  
                {'name': 'data',                'len': None},  
                ]
            },  
        b'\x64\x12':{ 
            'name': ZpiCommand.AF_DATA_RETRIEVE_SRSP,
            'structure':[
                {'name': 'status',              'len': 1},
                {'name': 'len',                 'len': 1},  
                {'name': 'data',                'len': None},  
                ]
            },    
        b'\x64\x13':{ 
            'name': ZpiCommand.AF_APSF_CONFIG_SET_SRSP,
            'structure':[
                {'name': 'status',              'len': 1},
                ]
            }, 
          
        #-----------------------------------------------------------------------                          
        #ZDO interface
        #----------------------------------------------------------------------- 
        b'\x65\x00':{ 
            'name': ZpiCommand.ZDO_NWK_ADDR_REQ_SRSP,
            'structure':[
                {'name': 'status',              'len': 1},
                ]
            },
        b'\x65\x01':{ 
            'name': ZpiCommand.ZDO_IEEE_ADDR_REQ_SRSP,
            'structure':[
                {'name': 'status',              'len': 1},
                ]
            },        
        b'\x65\x02':{ 
            'name': ZpiCommand.ZDO_NODE_DESC_REQ_SRSP,
            'structure':[
                {'name': 'status',              'len': 1},
                ]
            }, 
        b'\x65\x03':{ 
            'name': ZpiCommand.ZDO_POWER_DESC_REQ_SRSP,
            'structure':[
                {'name': 'status',              'len': 1},
                ]
            }, 
        b'\x65\x04':{ 
            'name': ZpiCommand.ZDO_SIMPLE_DESC_REQ_SRSP,
            'structure':[
                {'name': 'status',              'len': 1},
                ]
            }, 
        b'\x65\x05':{ 
            'name': ZpiCommand.ZDO_ACTIVE_EP_REQ_SRSP,
            'structure':[
                {'name': 'status',              'len': 1},
                ]
            }, 
        b'\x65\x06':{ 
            'name': ZpiCommand.ZDO_MATCH_DESC_REQ_SRSP,
            'structure':[
                {'name': 'status',              'len': 1},
                ]
            },   
        b'\x65\x07':{ 
            'name': ZpiCommand.ZDO_COMPLEX_DESC_REQ_SRSP,
            'structure':[
                {'name': 'status',              'len': 1},
                ]
            },       
        b'\x65\x08':{ 
            'name': ZpiCommand.ZDO_USER_DESC_REQ_SRSP,
            'structure':[
                {'name': 'status',              'len': 1},
                ]
            }, 
        b'\x65\x0a':{ 
            'name': ZpiCommand.ZDO_DEVICE_ANNCE_SRSP,
            'structure':[
                {'name': 'status',              'len': 1},
                ]
            }, 
        b'\x65\x0b':{ 
            'name': ZpiCommand.ZDO_USER_DESC_SET_SRSP,
            'structure':[
                {'name': 'status',              'len': 1},
                ]
            },                
        b'\x65\x0c':{ 
            'name': ZpiCommand.ZDO_SERVER_DESC_REQ_SRSP,
            'structure':[
                {'name': 'status',              'len': 1},
                ]
            }, 
        b'\x65\x20':{ 
            'name': ZpiCommand.ZDO_END_DEVICE_BIND_REQ_SRSP,
            'structure':[
                {'name': 'status',              'len': 1},
                ]
            },     
        b'\x65\x21':{ 
            'name': ZpiCommand.ZDO_BIND_REQ_SRSP,
            'structure':[
                {'name': 'status',              'len': 1},
                ]
            },        
        b'\x65\x22':{ 
            'name': ZpiCommand.ZDO_UNBIND_REQ_SRSP,
            'structure':[
                {'name': 'status',              'len': 1},
                ]
            }, 
        b'\x65\x30':{ 
            'name': ZpiCommand.ZDO_MGMT_NWK_DISC_REQ_SRSP,
            'structure':[
                {'name': 'status',              'len': 1},
                ]
            },          
        b'\x65\x31':{ 
            'name': ZpiCommand.ZDO_MGMT_LQI_REQ_SRSP,
            'structure':[
                {'name': 'status',              'len': 1},
                ]
            },  
        b'\x65\x32':{ 
            'name': ZpiCommand.ZDO_MGMT_RTG_REQ_SRSP,
            'structure':[
                {'name': 'status',              'len': 1},
                ]
            },  
        b'\x65\x33':{ 
            'name': ZpiCommand.ZDO_MGMT_BIND_REQ_SRSP,
            'structure':[
                {'name': 'status',              'len': 1},
                ]
            },   
        b'\x65\x34':{ 
            'name': ZpiCommand.ZDO_MGMT_LEAVE_REQ_SRSP,
            'structure':[
                {'name': 'status',              'len': 1},
                ]
            },    
        b'\x65\x35':{ 
            'name': ZpiCommand.ZDO_MGMT_DIRECT_JOIN_REQ_SRSP,
            'structure':[
                {'name': 'status',              'len': 1},
                ]
            },  
        b'\x65\x36':{ 
            'name': ZpiCommand.ZDO_MGMT_PERMIT_JOIN_REQ_SRSP,
            'structure':[
                {'name': 'status',              'len': 1},
                ]
            },      
        b'\x65\x37':{ 
            'name': ZpiCommand.ZDO_MGMT_NWK_UPDATE_REQ_SRSP,
            'structure':[
                {'name': 'status',              'len': 1},
                ]
            },    
        b'\x65\x40':{ 
            'name': ZpiCommand.ZDO_STARTUP_FROM_APP_SRSP,
            'structure':[
                {'name': 'status',              'len': 1},
                ]
            },  
        b'\x65\x23':{ 
            'name': ZpiCommand.ZDO_SET_LINK_KEY_SRSP,
            'structure':[
                {'name': 'status',              'len': 1},
                ]
            },  
        b'\x65\x24':{ 
            'name': ZpiCommand.ZDO_REMOVE_LINK_KEY_SRSP,
            'structure':[
                {'name': 'status',              'len': 1},
                ]
            },    
        b'\x65\x25':{ 
            'name': ZpiCommand.ZDO_GET_LINK_KEY_SRSP,
            'structure':[
                {'name': 'status',              'len': 1},
                ]
            },   
        b'\x65\x26':{ 
            'name': ZpiCommand.ZDO_NWK_DISCOVERY_REQ_SRSP,
            'structure':[
                {'name': 'status',              'len': 1},
                ]
            },   
        b'\x65\x27':{ 
            'name': ZpiCommand.ZDO_JOIN_REQ_SRSP,
            'structure':[
                {'name': 'status',              'len': 1},
                ]
            }, 
        b'\x45\x80':{ 
            'name': ZpiCommand.ZDO_NWK_ADDR_RSP,
            'structure':[
                {'name': 'status',              'len': 1},
                {'name': 'ieee_addr',           'len': 8},
                {'name': 'nwk_addr',            'len': 2},
                {'name': 'start_index',         'len': 1},
                {'name': 'assoc_dev_num',       'len': 1},
                {'name': 'assoc_dev_list',      'len': None}, #TODO: also can use len_calc()?
                ]
            },   
        b'\x45\x81':{ 
            'name': ZpiCommand.ZDO_IEEE_ADDR_RSP,
            'structure':[
                {'name': 'status',              'len': 1},
                {'name': 'ieee_addr',           'len': 8},
                {'name': 'nwk_addr',            'len': 2},
                {'name': 'start_index',         'len': 1},
                {'name': 'assoc_dev_num',       'len': 1},
                {'name': 'assoc_dev_list',      'len': None},
                ]
            },        
        b'\x45\x82':{ 
            'name': ZpiCommand.ZDO_NODE_DESC_RSP,
            'structure':[
                {'name': 'src_addr',            'len': 2},
                {'name': 'status',              'len': 1},
                {'name': 'nwk_addr',            'len': 2},
                {'name': 'logical_type_flags',  'len': 1},
                {'name': 'aps_flags',           'len': 1},
                {'name': 'mac_cap_flags',       'len': 1}, 
                {'name': 'mnfr_code',           'len': 2}, 
                {'name': 'max_buf_size',        'len': 1}, 
                {'name': 'max_trans_size',      'len': 2}, 
                {'name': 'server_mask',         'len': 2}, 
                {'name': 'max_out_trans_size',  'len': 2}, 
                {'name': 'descriptor_cap',      'len': 1}, 
                ]
            },   
        b'\x45\x83':{ 
            'name': ZpiCommand.ZDO_POWER_DESC_RSP,
            'structure':[
                {'name': 'src_addr',            'len': 2},
                {'name': 'status',              'len': 1},
                {'name': 'nwk_addr',            'len': 2},
                {'name': 'cur_pwrmode_avail_pwrsrc',  'len': 1},
                {'name': 'cur_pwrsrc_and_level',      'len': 1},
                ]
            },      
        b'\x45\x84':{ 
            'name': ZpiCommand.ZDO_SIMPLE_DESC_RSP,
            'structure':[
                {'name': 'src_addr',            'len': 2},
                {'name': 'status',              'len': 1},
                {'name': 'nwk_addr',            'len': 2},

                #this len field indicate if there is a simple descriptor followed. TODO: need check this
                {'name': 'len',                 'len': 1},
                {'name': 'endpoint',            'len': 1},
                {'name': 'profile_id',          'len': 2}, 
                {'name': 'device_id',           'len': 2}, 
                {'name': 'device_ver',          'len': 1}, 
                {'name': 'in_cluster_num',      'len': 1},
                {'name': 'in_cluster_list',     'len': ('in_cluster_num', '2*x')},
                {'name': 'out_cluster_num',     'len': 1}, 
                {'name': 'out_cluster_list',    'len': None},  #TODO: use len_calc
                ]
            },  
        b'\x45\x85':{ 
            'name': ZpiCommand.ZDO_ACTIVE_EP_RSP,
            'structure':[
                {'name': 'src_addr',            'len': 2},
                {'name': 'status',              'len': 1},
                {'name': 'nwk_addr',            'len': 2},
                {'name': 'active_ep_cnt',       'len': 1},
                {'name': 'active_ep_list',      'len': None},
                ]
            },          
        b'\x45\x86':{ 
            'name': ZpiCommand.ZDO_MATCH_DESC_RSP,
            'structure':[
                {'name': 'src_addr',            'len': 2},
                {'name': 'status',              'len': 1},
                {'name': 'nwk_addr',            'len': 2},
                {'name': 'match_len',           'len': 1},
                {'name': 'match_list',          'len': None},
                ]
            },   
        b'\x45\x90':{
            'name': ZpiCommand.ZDO_COMPLEX_DESC_RSP,
            'structure':[
                {'name': 'src_addr',            'len': 2},
                {'name': 'status',              'len': 1},
                {'name': 'nwk_addr',            'len': 2},
                {'name': 'complex_len',         'len': 1},
                {'name': 'complex_list',        'len': None},
                ]
            },   
        b'\x45\x91':{
            'name': ZpiCommand.ZDO_USER_DESC_RSP,
            'structure':[
                {'name': 'src_addr',            'len': 2},
                {'name': 'status',              'len': 1},
                {'name': 'nwk_addr',            'len': 2},
                {'name': 'len',                 'len': 1},
                {'name': 'user_descriptor',     'len': None},
                ]
            },          
        b'\x45\x94':{
            'name': ZpiCommand.ZDO_USER_DESC_CONF,
            'structure':[
                {'name': 'src_addr',            'len': 2},
                {'name': 'status',              'len': 1},
                {'name': 'nwk_addr',            'len': 2},
                ]
            },        
        b'\x45\x95':{
            'name': ZpiCommand.ZDO_SERVER_DESC_RSP,
            'structure':[
                {'name': 'src_addr',            'len': 2},
                {'name': 'status',              'len': 1},
                {'name': 'server_mask',         'len': 2},
                ]
            },     
        b'\x45\xa0':{ 
            'name': ZpiCommand.ZDO_END_DEVICE_BIND_RSP,
            'structure':[
                {'name': 'src_addr',            'len': 2},
                {'name': 'status',              'len': 1},
                ]
            },                     
        b'\x45\xa1':{ 
            'name': ZpiCommand.ZDO_BIND_RSP,
            'structure':[
                {'name': 'src_addr',            'len': 2},
                {'name': 'status',              'len': 1},
                ]
            },   
        b'\x45\xa2':{ 
            'name': ZpiCommand.ZDO_UNBIND_RSP,
            'structure':[
                {'name': 'src_addr',            'len': 2},
                {'name': 'status',              'len': 1},
                ]
            },  
        b'\x45\xb0':{ 
            'name': ZpiCommand.ZDO_MGMT_NWK_DISC_RSP,
            'structure':[
                {'name': 'src_addr',            'len': 2},
                {'name': 'status',              'len': 1},
                {'name': 'nwk_cnt',             'len': 1},
                {'name': 'start_index',         'len': 1},
                {'name': 'nwk_list_cnt',        'len': 1},
                {'name': 'nwk_list_records',    'len': None}, #TODO: 6*nwk_list_cnt
                ]
            },      
        b'\x45\xb1':{ 
            'name': ZpiCommand.ZDO_MGMT_LQI_RSP,
            'structure':[
                {'name': 'src_addr',            'len': 2},
                {'name': 'status',              'len': 1},
                {'name': 'nbr_table_entries',   'len': 1},
                {'name': 'start_index',         'len': 1},
                {'name': 'nbr_table_list_cnt',  'len': 1},
                {'name': 'nbr_table_list_records',    'len': None}, #TODO: 22*nwk_list_cnt
                ]
            },               
        b'\x45\xb2':{ 
            'name': ZpiCommand.ZDO_MGMT_RTG_RSP,
            'structure':[
                {'name': 'src_addr',            'len': 2},
                {'name': 'status',              'len': 1},
                {'name': 'rtg_table_entries',   'len': 1},
                {'name': 'start_index',         'len': 1},
                {'name': 'rtg_table_list_cnt',  'len': 1},
                {'name': 'rtg_table_list_records',    'len': None}, #TODO: 5*nwk_list_cnt
                ]
            },  
        b'\x45\xb3':{ 
            'name': ZpiCommand.ZDO_MGMT_BIND_RSP,
            'structure':[
                {'name': 'src_addr',            'len': 2},
                {'name': 'status',              'len': 1},
                {'name': 'binding_table_entries',   'len': 1},
                {'name': 'start_index',         'len': 1},
                {'name': 'binding_table_list_cnt',  'len': 1},
                {'name': 'binding_table_list_records',    'len': None}, #TODO: 20*nwk_list_cnt
                ]
            },    
        b'\x45\xb4':{ 
            'name': ZpiCommand.ZDO_MGMT_LEAVE_RSP,
            'structure':[
                {'name': 'src_addr',            'len': 2},
                {'name': 'status',              'len': 1},
                #{'name': 'dummy',               'len': 3}     #as tested, ZDO_MGMT_LEAVE_RSP return 3 more 0x00 bytes if the remote device doesn't support generate this request
                ]
            },        
        b'\x45\xb5':{ 
            'name': ZpiCommand.ZDO_MGMT_DIRECT_JOIN_RSP,
            'structure':[
                {'name': 'src_addr',            'len': 2},
                {'name': 'status',              'len': 1},
                ]
            },          
        b'\x45\xb6':{ 
            'name': ZpiCommand.ZDO_MGMT_PERMIT_JOIN_RSP,
            'structure':[
                {'name': 'src_addr',            'len': 2},
                {'name': 'status',              'len': 1},
                ]
            },        
        b'\x45\xc0':{ 
            'name': ZpiCommand.ZDO_STATE_CHANGE_IND,
            'structure':[
                {'name': 'state',               'len': 1},
                ]
            },        
        b'\x45\xc1':{ 
            'name': ZpiCommand.ZDO_END_DEVICE_ANNCE_IND,
            'structure':[
                {'name': 'src_addr',            'len': 2},
                {'name': 'nwk_addr',            'len': 2},
                {'name': 'ieee_addr',           'len': 8},
                {'name': 'cap',                 'len': 1}, #capabilities
                ]
            },      
        b'\x45\xc2':{ 
            'name': ZpiCommand.ZDO_MATCH_DESC_RSP_SENT,
            'structure':[
                {'name': 'nwk_addr',            'len': 2},
                {'name': 'in_cluster_num',      'len': 1},
                #Must add calculation to resolve the variable length issue
                {'name': 'in_cluster_list',     'len': ('in_cluster_num', '2*x')},  
                {'name': 'out_cluster_num',     'len': 1},
                {'name': 'out_cluster_list',    'len': None}, #TODO:?
                ]
            },  
        b'\x45\xc3':{ 
            'name': ZpiCommand.ZDO_STATUS_ERROR_RSP,
            'structure':[
                {'name': 'src_addr',            'len': 2},
                {'name': 'status',              'len': 1},
                ]
            },         
        b'\x45\xc4':{ 
            'name': ZpiCommand.ZDO_SRC_RTG_IND,
            'structure':[
                {'name': 'dst_addr',            'len': 2},
                {'name': 'relay_cnt',           'len': 1},
                {'name': 'relay_list',          'len': None}, #TODO:?
                ]
            },   
        b'\x45\xc9':{ 
            'name': ZpiCommand.ZDO_LEAVE_IND,
            'structure':[
                {'name': 'src_addr',            'len': 2},
                {'name': 'ext_addr',            'len': 8},
                {'name': 'request',             'len': 1},
                {'name': 'remove',              'len': 1},
                {'name': 'rejoin',              'len': 1},
                ]
            },         
        b'\x65\x3e':{ 
            'name': ZpiCommand.ZDO_MSG_CB_REGISTER_SRSP,
            'structure':[
                {'name': 'status',              'len': 1},
                ]
            },
        b'\x65\x3f':{ 
            'name': ZpiCommand.ZDO_MSG_CB_REMOVE_SRSP,
            'structure':[
                {'name': 'status',              'len': 1},
                ]
            },       
        b'\x45\xff':{ 
            'name': ZpiCommand.ZDO_MSG_CB_INCOMING,
            'structure':[
                {'name': 'src_addr',            'len': 2},
                {'name': 'was_broadcast',       'len': 1},
                {'name': 'cluster_id',          'len': 2},
                {'name': 'security_use',        'len': 1},
                {'name': 'seq_num',             'len': 1},
                {'name': 'mac_dst_addr',        'len': 2},
                {'name': 'data',                'len': None},
                ]
            },                                                                          
        #-----------------------------------------------------------------------               
        #Util interface     
        #-----------------------------------------------------------------------        
        b'\x67\x11':{ 
            'name': ZpiCommand.UTIL_DATA_REQ_SRSP,
            'structure':[
                {'name': 'status',              'len': 1},
                ]
            },
        b'\x67\x40':{ 
            'name': ZpiCommand.UTIL_ADDRMGR_EXT_ADDR_LOOKUP_SRSP,
            'structure':[
                {'name': 'nwk_addr',            'len': 2},
                ]
            },
        b'\x67\x41':{ 
            'name': ZpiCommand.UTIL_ADDRMGR_NWK_ADDR_LOOKUP_SRSP,
            'structure':[
                {'name': 'ext_addr',            'len': 8},
                ]
            },
        b'\x67\x44':{ 
            'name': ZpiCommand.UTIL_APSME_LINK_KEY_DATA_GET_SRSP,
            'structure':[
                {'name': 'status',              'len': 1},
                {'name': 'sec_key',             'len': 16},
                {'name': 'tx_frm_cntr',         'len': 4},
                {'name': 'rx_frm_cntr',         'len': 4},
                ]
            },
        b'\x67\x45':{ 
            'name': ZpiCommand.UTIL_APSME_LINK_KEY_NV_ID_GET_SRSP,
            'structure':[
                {'name': 'status',              'len': 1},
                {'name': 'link_key_nv_id',      'len': 2},
                ]
            },
        b'\x67\x4b':{ 
            'name': ZpiCommand.UTIL_APSME_REQUEST_KEY_CMD_SRSP,
            'structure':[
                {'name': 'status',              'len': 1},
                ]
            },
        b'\x67\x48':{ 
            'name': ZpiCommand.UTIL_ASSOC_COUNT_SRSP,
            'structure':[
                {'name': 'count',               'len': 2},
                ]
            },     
        b'\x67\x49':{ 
            'name': ZpiCommand.UTIL_ASSOC_FIND_DEVICE_SRSP,
            'structure':[
                {'name': 'device',              'len': 18}, #contains sub-fields
                ]
            },  
        b'\x67\x80':{ 
            'name': ZpiCommand.UTIL_ZCL_KEY_EST_INIT_EST_SRSP,
            'structure':[
                {'name': 'status',              'len': 1},
                ]
            },    
        b'\x67\x81':{ 
            'name': ZpiCommand.UTIL_ZCL_KEY_EST_SIGN_SRSP,
            'structure':[
                {'name': 'status',              'len': 1},
                {'name': 'key',                 'len': 42},
                ]
            },           
        b'\x67\x10':{ 
            'name': ZpiCommand.UTIL_TEST_LOOPBACK_SRSP,
            'structure':[
                {'name': 'test_data',           'len': None},
                ]
            },   
                     
        #APS extended
        b'\x6f\x00':{ 
            'name': ZpiCommand.APS_ADD_GROUP_SRSP,
            'structure':[
                {'name': 'status',           'len': 1},
                ]
            },   
        b'\x6f\x01':{ 
            'name': ZpiCommand.APS_REMOVE_GROUP_SRSP,
            'structure':[
                {'name': 'status',           'len': 1},
                ]
            },   
        b'\x6f\x02':{ 
            'name': ZpiCommand.APS_REMOVE_ALL_GROUP_SRSP,
            'structure':[
                {'name': 'status',           'len': 1},
                ]
            },     
        b'\x6f\x03':{ 
            'name': ZpiCommand.APS_FIND_GROUP_SRSP,
            'structure':[
                {'name': 'status',           'len': 1},
                {'name': 'endpoint',         'len': 1},
                {'name': 'group_id',         'len': 2},
                {'name': 'group_name',       'len': 16},
                ]
            },   
        b'\x6f\x04':{ 
            'name': ZpiCommand.APS_FIND_ALL_GROUPS_FOR_EP_SRSP,
            'structure':[
                {'name': 'status',           'len': 1},
                {'name': 'endpoint',         'len': 1},
                {'name': 'group_cnt',        'len': 1},
                {'name': 'group_id_list',    'len': ('group_cnt', '2*x')},
                ]
            }, 
        b'\x6f\x05':{ 
            'name': ZpiCommand.APS_COUNT_ALL_GROUPS_SRSP,
            'structure':[
                {'name': 'status',           'len': 1},
                {'name': 'group_cnt',        'len': 1},
                ]
            },   
                                                    
        }
    