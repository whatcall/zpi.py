""" 
    CC2530-ZNP firmware radio tests
"""
import sys
import serial
#import struct
import time
import threading

import logging
log = logging.getLogger('drivers.zpi_zpi.zpi_test')
console = logging.StreamHandler()
#formatter = logging.Formatter('[%(asctime)s]:%(name)s - %(message)s')
formatter = logging.Formatter('[%(asctime)s] %(message)s')
console.setFormatter(formatter)
log.addHandler(console)
log.setLevel(logging.INFO)

from zpi import * 
from zpi import ZpiCommand

#global constants
#SERIAL_PORT = 'COM11'    #Router  
SERIAL_PORT = 'COM13'  #Coordinator
#SERIAL_PORT = 'COM11'  #Router
#SERIAL_PORT = 'COM8'   #This USB adapter seems not always working...
BAUDRATE = 115200

#device configuration
DEVICE_TYPES = ('coordinator', 'router', 'light', 'switch')
ZCL_HA_PROFILE_ID = 0x0104
#application definition running on endpoints
SAMPLE_SWITCH = {
    'name': 'onoff switch sample',
    'endpoint': 10,
    'profile_id': ZCL_HA_PROFILE_ID,
    'device_id': 0x0000, #HA: OnOff Switch
    'device_ver': 0x01,  #Mnfr define   
    'in_clusters': [],
    'out_clusters': [0x0006]          
    }

SAMPLE_LIGHT = {
    'name': 'onoff light sample',
    'endpoint': 11,
    'profile_id': ZCL_HA_PROFILE_ID,
    'device_id': 0x0100, #HA: OnOff Light
    'device_ver': 0x00,  #Mnfr define    
    'in_clusters': [0x0006],
    'out_clusters': [],            
    } 



sapi_apps = {
    'endpoint': 1,
    'profile_id': ZCL_HA_PROFILE_ID,
    
    'coordinator':{
        'device_id': 0x0005, #HA: Configuration tool
        'device_ver': 0x00,  #Mnfr define     
        'in_commands':[],
        'out_commands':[],   
        },
    'router':{
        'device_id': 0x0008, #HA: Range extender
        'device_ver': 0x00,  #Mnfr define    
        'in_commands':[],
        'out_commands':[], 
        },    
    'switch':{
        'device_id': 0x0000, #HA: OnOff Switch
        'device_ver': 0x01,  #Mnfr define   
        'in_commands':[],
        'out_commands':[0x0001, 0x0002],   
        },
    'light':{
        'device_id': 0x0100, #HA: OnOff Light
        'device_ver': 0x00,  #Mnfr define    
        'in_commands':[0x0001, 0x0002],
        'out_commands':[], 
        },
    }

#global vars

logical_type = LogicalType.COORDINATOR
device_type = 'coordinator'
device_info = {
    'nwk_addr':0x0000,      #need update after initializing
    'ieee_addr': 0x0,       #need update
    'profile_id': ZCL_HA_PROFILE_ID,
    }

device_app = None
device_app_bind = None
device_apps = [device_app]

zb_send_data_conf_cnt = 0
zb_send_data_req_cnt = 0

sys_reset_indicated = threading.Event()
zb_start_confirmed = threading.Event()
zb_send_data_confirmed = threading.Event()
zb_receive_data_indicated = threading.Event()
zb_allow_bind_confirmed = threading.Event()
zb_bind_confirmed = threading.Event()

af_data_confirmed = threading.Event()
af_data_conf_cnt = 0
af_data_req_cnt = 0

zdo_node_desc_responded = threading.Event()
zdo_power_desc_responded = threading.Event()
zdo_active_ep_desc_responded = threading.Event()

#AREQ event and data for callback notifications, 
#assign one flag each for individual cmd type
zpi_areq_events = {}
ZPI_AREQ_EVENT_WAITING_TIMEOUT = 3.000  #3 secs

#rx_data is not queued for the same zpi_cmd type
zpi_areq_data = {}

def zpi_areq_event_clear(zpi_cmd):
    """ clear the zpi_cmd AREQ event """
    global zpi_areq_events
    if zpi_cmd in zpi_areq_events:
        zpi_areq_events[zpi_cmd].clear() 

def zpi_areq_event_set(zpi_cmd):
    """ set zpi_cmd event """
    global zpi_areq_events
    if zpi_cmd not in zpi_areq_events:
        zpi_areq_events[zpi_cmd] = threading.Event()
        
    zpi_areq_events[zpi_cmd].set()
    
def zpi_areq_event_wait(zpi_cmd, timeout = ZPI_AREQ_EVENT_WAITING_TIMEOUT):
    """ wait the zpi_cmd event """
    global zpi_areq_events
    if zpi_cmd not in zpi_areq_events:
        zpi_areq_events[zpi_cmd] = threading.Event()
        
    return zpi_areq_events[zpi_cmd].wait(timeout)

def zpi_areq_data_set(zpi_cmd, rx_data):
    """ set the zpi_areq_data with rx_data """
    #TODO:need lock ??
    global zpi_areq_data
    zpi_areq_data[zpi_cmd] = rx_data
    
def zpi_areq_data_get(zpi_cmd):
    """ get the zpi_areq_data of zpi_cmd """
    #TODO:need lock ??    
    global zpi_areq_data
    if zpi_cmd in zpi_areq_data:
        return zpi_areq_data[zpi_cmd]
    else:
        return None

def zpi_sys_reset_test(zpi, serial_port):
    """local device reset request"""
    log.info('Reset the CC2530-ZNP module...')
    
    zpi.sys_reset_req(ResetType.SOFT_RESET)
    if not sys_reset_indicated.wait(2.000):         #soft reset need ~0.600 seconds
        log.error('Start reset indication waiting timeout!')
        zpi.halt()
        serial_port.close()
        sys.exit()
    
def zpi_sys_version_test(zpi):
    """ get local device system version test """
    log.info('Request ZNP system version...')
    try:
        (transport_rev, product_id, major_rel, minor_rel, 
            maint_rel) = zpi.sys_version()
        log.info('TransportRev=%s, ProductId=%s, SwRev=%s.%s.%s', 
                 transport_rev, product_id, major_rel, minor_rel, maint_rel)
    except:
        log.error('Failed')  

def zpi_sys_read_adc_test(zpi):
    """ system read adc test """
    log.info('Read Adc channel 6...')
    try:
        adc_value = zpi.sys_adc_read(6, AdcResolution._12_BIT)
        log.info('ADC value = 0x%.3X', adc_value)
    except:
        log.error('Failed')

def zpi_sys_gpio_test(zpi):
    """ system gpio test """
    log.info('Read Gpio pins...')
    try:
        gpio_value = zpi.sys_gpio(GpioOperation.READ, 0x00)
        log.info('GPIO value = 0x%.2X', gpio_value)
    except:
        log.error('Failed')
    
def zpi_sys_random_test(zpi):
    """ system random test """
    log.info('Get a random value...')
    try:
        random_value = zpi.sys_random()
        log.info('Random value = 0x%.4X', random_value)
    except:
        log.error('Failed')
        
def zpi_zb_get_device_info_test(zpi):
    """ get device information: PanID, NwkAddr, Channel etc. """
    log.info('Get device information...')
    try:
        device_state = zpi.zb_get_device_info(DeviceInfoParameter.STATE)
        channel = zpi.zb_get_device_info(DeviceInfoParameter.CHANNEL)
        pan_id = zpi.zb_get_device_info(DeviceInfoParameter.PAN_ID)
        ext_pan_id = zpi.zb_get_device_info(DeviceInfoParameter.EXT_PAN_ID)
        nwk_addr = zpi.zb_get_device_info(DeviceInfoParameter.NWK_ADDR)
        ieee_addr = zpi.zb_get_device_info(DeviceInfoParameter.IEEE_ADDR)

        log.info('Device State: %s', DeviceState.get_name(device_state))
        log.info('Channel=%d, PanID=0x%0.4X, PanIdExt=0x%0.16X,' %  (channel, 
            pan_id, ext_pan_id))
        log.info('NwkAddr=0x%0.4X, IeeeAddr=0x%0.16X' % (nwk_addr, ieee_addr))
    except:
        log.error('Failed!')
 
def zpi_zb_read_config_test(zpi):
    """ zb_read_config test """
    #read some configurations from ZNP device for future checking usage
    log.info('Read configuration parameters (ZCD_NV_XXX)...')
    try:
        status, _logical_type = zpi.zb_read_config(ConfigParameter.Device.ZCD_NV_LOGICAL_TYPE)
        if status != ZpiStatus.Z_SUCCESS:
            raise Exception()
        
        status, _zcd_nv_pan_id = zpi.zb_read_config(ConfigParameter.Network.ZCD_NV_PANID)
        if status != ZpiStatus.Z_SUCCESS:
            raise Exception()
        
        status, _zcd_nv_channel_list = zpi.zb_read_config(ConfigParameter.Network.ZCD_NV_CHANLIST) 
        if status != ZpiStatus.Z_SUCCESS:
            raise Exception()
        
        log.info('LOGICAL_TYPE = %s, PANID = 0x%0.4X, CHANLIST = 0x%0.8X', 
                 LogicalType.get_description(_logical_type), 
                 _zcd_nv_pan_id,
                 _zcd_nv_channel_list)
    except:
        log.error('Failed')
             
def zpi_zb_write_config_test(zpi, logical_type, 
                             startup_clear_state = False,
                             startup_clear_config = False):
    """  
        Configuration interface
        write minimal configuration set: logical_type, pan_id, channel_list when
        first time startup. 
    """
    log.info('Write configuration parameters (ZCD_NV_XXX)...')
    status = ZpiStatus.Z_SUCCESS
    try:
        zcd_nv_pan_id = 0xffff              #auto-select
        zcd_nv_channel_list = 0x00001000    #set 1 channel for testing only!
        log.info('LOGICAL_TYPE = %s, PANID = 0x%0.4X, CHANLIST = 0x%0.8X', 
            LogicalType.get_description(logical_type),
            zcd_nv_pan_id,
            zcd_nv_channel_list)
        
        status = zpi.zb_write_config(ConfigParameter.Device.ZCD_NV_LOGICAL_TYPE, 
                                     logical_type)
        if status != ZpiStatus.Z_SUCCESS:
            raise Exception('ZCD_NV_LOGICAL_TYPE')
        
        status = zpi.zb_write_config(ConfigParameter.Network.ZCD_NV_PANID, 
                                     zcd_nv_pan_id)
        if status != ZpiStatus.Z_SUCCESS:
            raise Exception('ZCD_NV_PANID')
        
        status = zpi.zb_write_config(ConfigParameter.Network.ZCD_NV_CHANLIST, 
                                     zcd_nv_channel_list) 
        if status != ZpiStatus.Z_SUCCESS:
            raise Exception('ZCD_NV_CHANLIST')

        #check startup options
        startup_option = StartupOption.NONE_MASK
        if startup_clear_state:
            startup_option = startup_option + StartupOption.CLEAR_STATE_MASK 
        if startup_clear_config:
            startup_option = startup_option + StartupOption.CLEAR_CONFIG_MASK 
        #write startup clear options and wait reset again
        status = zpi.zb_write_config(ConfigParameter.Device.ZCD_NV_STARTUP_OPTION, 
                                     startup_option)
        
        if status != ZpiStatus.Z_SUCCESS:
            raise Exception('ZCD_NV_STARTUP_OPTION')
    except Exception as e:
        log.error('Failed to write {0}. Status={1}'.format(e, status))
     
     
def zpi_zb_start_request_test(zpi, nwk_reset = False, 
                              logical_type = LogicalType.COORDINATOR):
    """ 
        test zb_start_request, 
        nwk_reset: if is True, ZNP needs to reset its network state.
    """    
    global  zb_start_confirmed

    #TODO:If network parameters changed, need to restart the device again with 
    #startup options clear-bits set to make the device clear its network state.      
    if nwk_reset:
        zpi_zb_write_config_test(zpi)
                
    log.info('SAPI start request...')
    try:
        zb_start_confirmed.clear()
        zpi.zb_start_request()  #need wait the ZB_START_CONF from ZNP
        if zb_start_confirmed.wait(5.000): #normal delay: ~700ms
            log.info('confirmed!')
        else:
            raise AreqTimeoutException('ZB_START_CONFIRM waiting timeout!')
    except:
        log.error('Cannot start the ZNP device!')
        return #quit    

def zpi_zb_app_reg_req_test(zpi):    
    """
        Simple API: use this Simple interface to register a default App endpoint 
        and then start the device
    """
    log.info('SAPI application register...')
    
    global sapi_apps
    device_app = sapi_apps[device_type]  
    
    log.info('ep=%d, profile_id=0x%.4X, device_id=0x%.4X, device_ver=0x%.4X' %
             (sapi_apps['endpoint'],
             sapi_apps['profile_id'], 
             device_app['device_id'], 
             device_app['device_ver']))
    log.info('in_commands:%s, out_commands:%s' %
             (device_app['in_commands'], device_app['out_commands']))  
    try:

        status = zpi.zb_app_register_request(endpoint = sapi_apps['endpoint'], 
                                             profile_id = sapi_apps['profile_id'], 
                                             device_id = device_app['device_id'], 
                                             device_ver = device_app['device_ver'], 
                                             in_commands = device_app['in_commands'], 
                                             out_commands = device_app['out_commands'])
        if ZpiStatus.Z_SUCCESS == status:
            log.info('Done!')
        else:
            log.warning('Failed! status = 0x%.2X' % status)
    except:        
        log.error('Failed!')
      
    
def zpi_zb_permit_joining_request_test(zpi, dst_addr, timeout):
    """ zb_permit_joining_request() test"""
    log.info('Permit Joining Request test...') 
    
    #the default permit joining is always on.
    zpi.zb_permit_joining_request(dst_addr, timeout)  
    
def zpi_zb_bind_device_test(zpi):
    """ zb_bind_device() test """
    log.info('Bind device test...')
    #first set router 1 in Allow Binding mode
    if device_type == 'light':  #this device should be launched before switch
        log.info('Set device in Allow Bind mode for 60 seconds.')
        zpi.zb_allow_bind(60)  #allow 60 seconds
        log.info('Waiting allow bind confirm...')
        #wait allow_bind_confirm for 60 seconds
        #global zb_allow_bind_confirmed
        #if zb_allow_bind_confirmed.wait(60):
        #    log.info('Bind request accepted.')
        #else:
        #    log.info('No bind request received in 60 seconds.')
        
    elif device_type == 'switch':
        log.info('Send Bind Device request with DstAddr = NULL.')
        global sapi_apps
        global zb_bind_confirmed
        
        zb_bind_confirmed.clear()
        zpi.zb_bind_device(BindAction.CREATE_BIND, sapi_apps['switch']['out_commands'][0])
        log.info('Waiting bind confirm...')
        if zb_bind_confirmed.wait(5.000):
            log.info('Bind confirmed.')
        else:
            log.info('Timeout.')
    else:
        log.info('No test executed.') 
  
  
def zpi_zb_transmit_test(zpi, dst_addr, handle, data):
    """ send data request through SAPI """
    global zb_send_data_req_cnt
    global zb_send_data_conf_cnt
    
    zb_send_data_confirmed.clear()
    zpi.zb_send_data_request(dst_addr_short = dst_addr, 
        cmd_id = 0x0001, 
        handle = handle, 
        tx_options = TxOptions.AF_DISC_ROUTE | TxOptions.AF_ACK_REQUEST, 
        radius = 0x00, 
        payload = data)
    handle = handle + 1  # increase handle for frame tracking
    if handle > 0xff:
        handle = 0x00
        
    #wait DATA confirmed
    if not zb_send_data_confirmed.wait(3.000):
        log.warning('No data confirm received!')


    zb_send_data_req_cnt = zb_send_data_req_cnt + 1
    #time.sleep(0.050)
    time.sleep(3.000)
    log.info('Request/Confirmed: [%s/%s]' % (
        zb_send_data_req_cnt, zb_send_data_conf_cnt))
  
  
def zpi_af_register_test(zpi):
    """ we could use af_register to register more than 1 endpoint apps """
    _app = None
    if device_type == 'light':
        _app = SAMPLE_LIGHT
    elif device_type == 'switch':
        _app = SAMPLE_SWITCH
    else:
        pass
        
    if _app is not None:
        log.info('Af register test...')
        log.info('App info:%s' % repr(_app))
        status = zpi.af_register(endpoint = _app['endpoint'],
                                 profile_id = _app['profile_id'],
                                 device_id = _app['device_id'],
                                 device_ver = _app['device_ver'],
                                 latency_req = LatencyReq.ZB_DEFAULT,
                                 in_clusters = _app['in_clusters'],
                                 out_clusters = _app['out_clusters'])   

        log.info('Status = %s', ZpiStatus.get_name(status))
        
def zpi_af_transmit_test(zpi):
    """ transmit data via AF interface. af_register() must be used to register
        at least one endpoint app before transmit data 
    """
    global device_type
    global af_data_confirmed
    global af_data_conf_cnt, af_data_req_cnt
    
    
    _app = None
    _dst_addr = 0x0000
    if device_type == 'light':
        _app = SAMPLE_LIGHT
        _app_dst = SAMPLE_SWITCH
        _cluster_id = _app['in_clusters'][0]
        _dst_addr = 0x22e9 #COM5-switch
    elif device_type == 'switch':
        _app = SAMPLE_SWITCH
        _app_dst = SAMPLE_LIGHT
        _cluster_id = _app['out_clusters'][0]
        _dst_addr = 0x0000 #0x4ab5 #COM11-light
    else:
        pass
    
    if _app is None:
        return    
    #AF_DATA_REQUEST, send message to a device with short nwk addr 
    zpi.af_data_request(dst_addr = _dst_addr,
                        dst_ep = _app_dst['endpoint'], 
                        src_ep = _app['endpoint'], 
                        cluster_id = _cluster_id, 
                        trans_id = 0x55, 
                        options = TxOptions.AF_ACK_REQUEST, 
                        radius = 0, 
                        data = 'toggle light')
    af_data_req_cnt = af_data_req_cnt + 1
    
    if af_data_confirmed.wait(1.000):
        af_data_conf_cnt = af_data_conf_cnt + 1
    else:
        log.warning('Wait AF data confirm timeout.')
    
    log.info('AF Data Request/Confirmed:[%d/%d]', af_data_req_cnt, af_data_conf_cnt)
        
    time.sleep(3.000)
    
    

def zpi_zdo_binding_test(zpi):
    """
        initialize bindings in 2 ways:
        - End device bind
        - Bind/Unbind
        
        SAPI can only bind to default endpoint, here we uses ZDO commands for 
        more options.
    """
    #get device info and profiles
    global device_type, dvice_app, device_app_bind
    
    if device_type == 'switch':
        device_app = SAMPLE_SWITCH
        device_app_bind = SAMPLE_LIGHT
    elif device_type == 'light':
        device_app = SAMPLE_LIGHT
        device_app_bind = SAMPLE_SWITCH
    else:
        pass
    
    #simulate an End-Device Bind, need 2 routers and one coordinator.
    #2 routes issue the EndDeviceBindRequest and the coordinator shall make
    #the match.
    #Procedure: 
    #    - Push one button on light to allow bind
    #    - Push one button on switch to bind
    status = zpi.zdo_end_device_bind_req(dst_addr = 0x0000, #coordinator 
                                        local_coordinator = device_info['nwk_addr'],
                                        endpoint = device_app['endpoint'],
                                        profile_id = device_info['profile_id'],
                                        in_clusters = device_app['in_clusters'],
                                        out_clusters = device_app['out_clusters'])
    
    if status != ZpiStatus.Z_SUCCESS:  
        log.warning('END_DEVICE_BIND_REQ failed! status = %s' % status)  
        return 
    
    #wait match response??
    
    
#    zpi.zdo_bind_req(dst_addr = device_info['nwk_addr'], #request its self
#                 src_addr = device_info['ieee_addr'], #64-bit bind src addr
#                 src_ep = SAMPLE_SWITCH['endpoint'],
#                 cluster_id = device_app['out'], #ZCL-OnOff cluster
#                 bind_addr_mode = AddressMode.ADDRESS_64_BIT,
#                 bind_addr = device_app_bind,
#                 bind_ep = device_app_bind['endpoint'])
   
     
def zpi_device_discovery_test(zpi, timeout = 10.0):
    """ 
        Discovery all devices in network and also mark activity.
        
        refer to TI SWRA203:"Method for Discovering Network Topology.pdf" 
        Steps:
            - (1) Send UTIL_ASSOC_COUNT, UTIL_ASSOC_FIND_DEVICE to get neighbors 
              and children devices of local device, assume the response result 
              is local_assoc_list
            - (2) Send ? request to get neighbor and children devices of device in
              local_assoc_list, assume the response of the n-th device  is 
              remote_assoc_list_n
            - (3) Merge remote_assoc_n with local and previous response list,
              Repeat (2) until every new device visited 
              
        Notes: 
            - (1) Local device may be any kind of logical device, typically a 
              coordinator.
            - (2) Remote request may only be sent to coordinator or router 
              device, because end device is not capable of associating new device
            - (3) Local Request must include all kind of relations to find all 
              of devices associated. 
            - (4) To reduce maintenance work after this time consumed discovery, 
              local application shall monitor the ZDP_DeviceAnnce message once
              new end device joined/rejoined the network. 
    """
    log.info('Discovery network devices...')
    #get local associated device, 
    local_assoc = []
    local_assoc_count = zpi.util_assoc_count(NodeRelation.PARENT, NodeRelation.OTHER)
    
    for assoc_index in range(0, local_assoc_count):
        device = zpi.util_assoc_find_device(assoc_index)

        #find the IEEE address for this device
        #For simple processing, we must enable ZCD_NV_ZDO_DIRECT_CB to receive 
        #all ZDO responses. Or we need to register all interested ZDO messages
        #one by one. 
        addr_short = device['addr_short']
        
        device['addr_long'] = zpi.zdo_ieee_addr_req(addr_short)
        
        
        #request descriptors: Node Descriptor, Power Descriptor, Active Endpoints
        log.info('Send ZDO_NODE_DESC_REQ to nwk_addr=0x%.4X', addr_short)
        zpi_areq_event_clear(ZpiCommand.ZDO_NODE_DESC_RSP)
        status = zpi.zdo_node_desc_req(dst_addr = addr_short, 
                                       nwk_addr_of_interest = addr_short) 
        if status!=ZpiStatus.Z_SUCCESS:
            log.warning('Failed.')
        else:
            log.info('wait ZDO_NODE_DESC_RSP...')
            if zpi_areq_event_wait(ZpiCommand.ZDO_NODE_DESC_RSP):
                rsp_result = zpi.zdo_node_desc_rsp_handler(zpi_areq_data_get(ZpiCommand.ZDO_NODE_DESC_RSP))
                device['node_desc'] = rsp_result
            else:
                log.warning('Response timeout.')   
            
        log.info('Send ZDO_POWER_DESC_REQ to nwk_addr=0x%.4X', addr_short)  
        zpi_areq_event_clear(ZpiCommand.ZDO_POWER_DESC_RSP)
        status = zpi.zdo_power_desc_req(dst_addr = addr_short, 
                                        nwk_addr_of_interest = addr_short)
        if status!=ZpiStatus.Z_SUCCESS:
            log.warning('Failed')
        else:
            log.info('wait ZDO_POWER_DESC_RSP...')
            if zpi_areq_event_wait(ZpiCommand.ZDO_POWER_DESC_RSP):
                rsp_result = zpi.zdo_power_desc_rsp_handler(zpi_areq_data_get(ZpiCommand.ZDO_POWER_DESC_RSP))
                device['power_desc'] = rsp_result
            else:
                log.warning('Response timeout.')  
                
            
        log.info('Send ZDO_ACTIVE_EP_REQ to nwk_addr=0x%.4X', addr_short)  
        zpi_areq_event_clear(ZpiCommand.ZDO_ACTIVE_EP_RSP)
        status = zpi.zdo_active_ep_req(dst_addr = addr_short, 
                                       nwk_addr_of_interest = addr_short) 
        if status!=ZpiStatus.Z_SUCCESS:
            log.warning('Failed')
        else:
            log.info('wait ZDO_ACTIVE_EP_RSP...')
            if zpi_areq_event_wait(ZpiCommand.ZDO_ACTIVE_EP_RSP):
                (src_addr, status, nwk_addr, active_eps) = zpi.zdo_active_ep_rsp_handler(zpi_areq_data_get(ZpiCommand.ZDO_ACTIVE_EP_RSP))
                device['active_ep'] = active_eps
            else:
                log.warning('Response timeout.') 
                
        log.info('Device#%d: ShortAddr=0x%.4X, Relation=%s, State=%s' % (
            assoc_index,                                                          
            device['addr_short'], 
            NodeRelation.get_name(device['node_relation']),
            DeviceState.get_name(device['dev_status'])
            ))
        #append current device to local associated list
        local_assoc.append(device)
        
    #request remote associated
    log.info('Request associated list of remote device...')
    remote_assoc = []
    
    #zpi.zdo_mgmt_lqi_req(device['addr_short'], 0)
    
    #construct network device list, according IEEE address???
    #TODO: determine active flag? 
    device_list = []
    device_list = device_list + local_assoc + remote_assoc
    
    #print all device found in whole network
    #TODO:
    
    return device_list
 
def zpi_service_discovery_test(zpi, device_list):
    """ discovery services running on network devices """
    #request Simple Descriptor for each active endpoint on specified device 
    #save the result as following format:
    #device_list[] -> device#n['endpoints'] ->endpoint#m->'simple_desc':
    #global device_list
    
    log.info('Service discovery...')
    for device in device_list:
        dst_addr = device['addr_short']
        
        if ('active_ep' not in device) or (device['active_ep'] is None):
            log.info('Ignore device = 0x%.4X, no active endpoints found.', dst_addr)
            continue
        
        log.info('Discovery device = 0x%.4X...', dst_addr)
        for endpoint in device['active_ep']:
            log.info('Send ZDO_SIMPLE_DESC_REQ for Endpoint[%d]...', endpoint)
            zpi_areq_event_clear(ZpiCommand.ZDO_SIMPLE_DESC_RSP)
            status = zpi.zdo_simple_desc_req(dst_addr = dst_addr,
                                             nwk_addr_of_interest = dst_addr,
                                             endpoint = endpoint)
            if status == ZpiStatus.Z_SUCCESS:
                if zpi_areq_event_wait(ZpiCommand.ZDO_SIMPLE_DESC_RSP):
                    rsp_result = zpi.zdo_simple_desc_rsp_handler(zpi_areq_data_get(ZpiCommand.ZDO_SIMPLE_DESC_RSP))
                    #save the result
                    print repr(rsp_result)
                    log.info('Receive ZDO_SIMPLE_DESC_RSP: ???')
                else:
                    log.warning('Response timeout.')
            else:
                log.warning('Failed.')
                
                
def zpi_aps_groups_test(zpi):
    """ test these functions: APS_COUNT_ALL_GROUPS """
    log.info('APS groups test...')

    log.info('add group...')
    endpoint = 1
    group_id = 0x0001
    log.info('Add 2 groups for endpoint %d', endpoint)
    status = zpi.aps_add_group(endpoint, group_id, 'group1')
    if status != ZpiStatus.Z_SUCCESS:  
        log.warning('Failure with status = %s', ZpiStatus.get_name(status))
    else:
        log.info('Add group 0x%.4X membership for endpoint %d', 
                 group_id, endpoint)
        
    group_id = group_id + 1
    status = zpi.aps_add_group(endpoint, group_id, 'group2')
    if status != ZpiStatus.Z_SUCCESS:  
        log.warning('Failure with status = %s', ZpiStatus.get_name(status))
    else:
        log.info('Add group 0x%.4X membership for endpoint %d', 
                 group_id, endpoint)
        
    endpoint = 2
    status = zpi.aps_add_group(endpoint, group_id, 'group3')
    if status != ZpiStatus.Z_SUCCESS:  
        log.warning('Failure with status = %s', ZpiStatus.get_name(status))
    else:
        log.info('Add group 0x%.4X membership for endpoint %d', 
                 group_id, endpoint)
        
    group_id = group_id + 1
    status = zpi.aps_add_group(endpoint, group_id, 'group4')
    if status != ZpiStatus.Z_SUCCESS:  
        log.warning('Failure with status = %s', ZpiStatus.get_name(status))
    else:
        log.info('Add group 0x%.4X membership for endpoint %d', 
                 group_id, endpoint)
        
    group_id = group_id + 1
    status = zpi.aps_add_group(endpoint, group_id, 'group4')
    if status != ZpiStatus.Z_SUCCESS:  
        log.warning('Failure with status = %s', ZpiStatus.get_name(status))
    else:
        log.info('Add group 0x%.4X membership for endpoint %d', 
                 group_id, endpoint)
        
    log.info('count all groups...')
    (status, group_cnt) = zpi.aps_count_all_groups()
    if status != ZpiStatus.Z_SUCCESS:  
        log.warning('Failure with status = %s', ZpiStatus.get_name(status))
    else:
        log.info('Read count of all groups=%d', group_cnt)
        
    log.info('find group...')    
    endpoint = 1
    group_id = 0x0001
    (status, _endpoint, _group_id, _group_name) = zpi.aps_find_group(endpoint, 
                                                                     group_id)
    if status != ZpiStatus.Z_SUCCESS:  
        log.warning('Failure with status = %s', ZpiStatus.get_name(status))
    else:
        log.info('Find group 0x%.4X of endpoint %d.Get name=%s ', _group_id, 
                 _endpoint, _group_name)    
    
    endpoint = 2
    group_id = group_id + 1
    
    (status, _endpoint, _group_id, _group_name) = zpi.aps_find_group(endpoint, 
                                                                     group_id)
    if status != ZpiStatus.Z_SUCCESS:  
        log.warning('Failure with status = %s', ZpiStatus.get_name(status))
    else:
        log.info('Find group 0x%.4X of endpoint %d.Get name=%s ', _group_id, 
                 _endpoint, _group_name)
        
        
    log.info('find all groups for an endpoint...')
    
    (status, _endpoint, _group_ids) = zpi.aps_find_all_groups_for_endpoint(endpoint) 
    if status != ZpiStatus.Z_SUCCESS:  
        log.warning('Failure with status = %s', ZpiStatus.get_name(status))
    else:
        log.info('Find all groups for endpoint=%d: group_ids=%s', _endpoint, 
                 repr(_group_ids))
        
    #remove group
    endpoint = 1
    status = zpi.aps_remove_all_group(endpoint)
    if status != ZpiStatus.Z_SUCCESS:  
        log.warning('Failure with status = %s', ZpiStatus.get_name(status))
    else:
        log.info('Removed all groups for endpoint=%d', endpoint)
       
    endpoint = 2                
    status = zpi.aps_remove_all_group(endpoint)
    if status != ZpiStatus.Z_SUCCESS:  
        log.warning('Failure with status = %s', ZpiStatus.get_name(status))
    else:
        log.info('Removed all groups for endpoint=%d', endpoint)
               
def zpi_callback(zpi, rx_data):
    """ 
        callback handler. Could be implemented as a dispatcher according
        incoming frame's id.
        
        TODO:We need specify individual callback for each message type.
    """
    global zb_send_data_confirmed
    global zb_start_confirmed
    global zb_send_data_conf_cnt
    global zb_allow_bind_confirmed
    global zb_bind_confirmed
    
    log.debug(80*'-')
    log.debug('RX [parsed]:')
    log.debug('id: %s' % rx_data['id'])
    for field_name, field_value in rx_data.iteritems():
        if field_name != 'id':
            log.debug('%s: %s' % (field_name, field_value.encode('hex')))
    log.debug(80*'-')
    
    
    if rx_data['id'] == ZpiCommand.ZB_SEND_DATA_CONFIRM:
        handle, status = zpi.zb_send_data_confirm_areq_handler(rx_data)
        handle = handle
        zb_send_data_confirmed.set()
        if ZpiStatus.Z_SUCCESS == status:
            zb_send_data_conf_cnt = zb_send_data_conf_cnt + 1
        else:
            log.warning('ZB Data Confirmed with unsuccessful value!')
            
    elif rx_data['id'] == ZpiCommand.ZB_RECEIVE_DATA_INDICATION:
        (src_addr, cmd, length, 
            data) = zpi.zb_receive_data_indication_areq_handler(rx_data)
        length = length
        log.info('ZB Receive Data:src_addr=0x%.4X,cmd=0x%.4X, data=%s' % (src_addr, 
            cmd, data.encode('hex')))
        zb_receive_data_indicated.set()
    
    elif rx_data['id'] == ZpiCommand.SYS_RESET_IND:
        (reason, transport_rev, product_id, major_rel, minor_rel, 
            hw_rev) = zpi.sys_reset_ind_handler(rx_data)
        reason = reason
        log.info('System reset successfully.')
        log.info('TransportRev=%s, ProductId=%s, SwRev=%s.%s, HwRev=%s', 
                 transport_rev, product_id, major_rel, minor_rel, hw_rev)
        sys_reset_indicated.set()
                    
    elif rx_data['id'] == ZpiCommand.ZB_START_CONFIRM:
        if ZpiStatus.Z_SUCCESS == zpi.zb_start_confirm_areq_handler(rx_data):
            zb_start_confirmed.set()
            
    elif rx_data['id'] == ZpiCommand.ZB_ALLOW_BIND_CONFIRM:
        src_addr = zpi.zb_allow_bind_confirm_handler(rx_data)
        log.info('Bind request from 0x%.4X responded.' % src_addr)
        zb_allow_bind_confirmed.set()
        
    elif rx_data['id'] == ZpiCommand.ZB_BIND_CONFIRM:
        (cmd_id, status) = zpi.zb_bind_confirm_handler(rx_data)
        log.info('Bind request confirmed with cmd_id=0x%.4X, status=%s.' % 
                 (cmd_id, ZpiStatus.get_name(status)))
        zb_bind_confirmed.set() 
    
    elif rx_data['id'] == ZpiCommand.AF_DATA_CONFIRM:
        #print 'AF_DATA_CONFRIM received'
        status, endpoint, trans_id = zpi.af_data_confirm_handler(rx_data)
        endpoint = endpoint
        trans_id = trans_id
        if status == ZpiStatus.Z_SUCCESS:
            af_data_confirmed.set()
        else:
            log.warning('AF data confirmed with failure status = %s', ZpiStatus.get_name(status))
        
    elif rx_data['id'] == ZpiCommand.AF_INCOMING_MSG:
        (group_id, cluster_id, src_addr, src_ep, dst_ep, was_broadcast,
            lqi, security_use, time_stamp, trans_seq, data) = zpi.af_incoming_msg_handler(rx_data)
        log.info("""AF_INCOMING_MSG:group_id=0x%.4X, cluster_id=0x%.4X,
            src_addr=0x%.4X, src_ep=%d, dst_ep=%d, was_broadcast=%d, lqi=%d, 
            security_use=%d, time_stamp=%d, trans_seq=%d, data=%s""",
            group_id, cluster_id, src_addr, src_ep, dst_ep, was_broadcast,
            lqi, security_use, time_stamp, trans_seq, repr(data))
    
    else:
        #for the rest received AREQs, set the data and fire the event
        print ('AREQ RX: %s' % rx_data['id'])
        for field_name, field_value in rx_data.iteritems():
            if field_name != 'id':
                print('%s: %s' % (field_name, field_value.encode('hex')))
                        
        zpi_areq_data_set(rx_data['id'], rx_data)
        zpi_areq_event_set(rx_data['id'])
        pass
            

 
def zpi_test_init():   
    #---------------------------------------------------------------------------
    # Create a serial port and init a ZPi instance
    #---------------------------------------------------------------------------
    if len(sys.argv) > 1:
        serial_name = sys.argv[1]
    else:
        serial_name = SERIAL_PORT
     
    global logical_type
    global device_type
    
    if (len(sys.argv) > 2 and 
        sys.argv[2] in DEVICE_TYPES):
        device_type = sys.argv[2] #set device_type with input args
        
    if device_type == 'coordinator':
        logical_type = LogicalType.COORDINATOR
    elif sys.argv[2] in ('router', 'light', 'switch'):
        logical_type = LogicalType.ROUTER
    else:
        logical_type = LogicalType.ENDDEVICE
        
    serial_port = serial.Serial(serial_name, BAUDRATE, timeout = 1.000)
    zpi = Zpi(serial_port, callback = zpi_callback)
    log.info('Open serial %s @ %dbps.' % (serial_port.portstr, serial_port.baudrate))
    
    return (zpi, serial_port)
    
def zpi_test_all():
    """ transmit a message to remote device """    
    global logical_type
    global device_list
    
    zpi, serial_port = zpi_test_init()
    
    zpi_sys_reset_test(zpi, serial_port) 
    zpi_sys_version_test(zpi)
    zpi_sys_read_adc_test(zpi)
    zpi_sys_gpio_test(zpi)
    zpi_sys_random_test(zpi)   
    
    zpi_zb_read_config_test(zpi)   
    zpi_zb_write_config_test(zpi, logical_type)
    zpi_zb_app_reg_req_test(zpi)
    zpi_af_register_test(zpi)    
    zpi_zb_start_request_test(zpi)
    zpi_zb_get_device_info_test(zpi)    
    
    try:
        zpi_aps_groups_test(zpi)
    except:
        log.warning('APS Group test failure!')
    #delay sometime for device rejoining if coordinator starting up with reset  
    #FIXME: always get device state = DEV_REJOIN even wait 5secs. ??? 
    time.sleep(1.000) 
    device_list = zpi_device_discovery_test(zpi)
    
    zpi_service_discovery_test(zpi, device_list)
    
    zpi_zb_bind_device_test(zpi)
    
        
    #---------------------------------------------------------------------------
    #Performance test result: Peer-to-peer, 82 data bytes, 65ms/msg
    #Local Host Processor<->Data Request<-> ZNP Router<--->(Dst Host Processor) 
    #---------------------------------------------------------------------------   
    log.info('ZB_SEND_DATA_REQUEST periodically:')
    handle = 0x55
    data = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ~!@#$'
    data = data + '%^&*()_+{}:"<>?' 
     
    if logical_type == LogicalType.COORDINATOR:
        dst_addr = 0x22e9
    else:
        dst_addr = 0x0000    
        
    while True:
        try:
            #zpi_zb_transmit_test(zpi, dst_addr, handle, data)
            zpi_af_transmit_test(zpi)
        except KeyboardInterrupt:
            log.info('Key pressed, ready to exit...')
            break
        except:
            log.error('Data request Error!')
            raise
            continue
    
    log.info('Kill the Zpi thread...')    
    zpi.halt()
    serial_port.close()
    log.info('Test exited.')

if __name__ == '__main__':        
    #
    #    accept sys.argv:
    #        SerialName -LogicalType
    #    example:
    #        COM5 -router
    import zpi
    zpi.set_debug(True)
    zpi_test_all()
    