"""
    zpi2.py: TI ZNP API v2 implementation module
"""
import struct
import datetime
import Queue
import threading

from zpi.frame import ZnpFrame
from zpi.command import *
from zpi.znp import Znp

__all__ = [
    'Zpi',
    'SerialTimeoutException',
    'AreqTimeoutException',
    'SrspTimeoutException',
    'ResetType',
    'ResetReason',
    'AdcResolution',
    'AddressMode',
    'GpioOperation',
    'ConfigParameter',
    'StartupOption',
    'LogicalType',
    'TxOptions',
    'AddressShort',
    'DeviceInfoParameter',
    'DeviceState',
    'NodeRelation',
    'BindAction',
    'LatencyReq',
    'ZpiStatus',
    'ZdoStartupFromAppStatus']

import logging
log = logging.getLogger('zpi.zpi2')
console = logging.StreamHandler()
formatter = logging.Formatter('[%(asctime)s] %(message)s')
console.setFormatter(formatter)
log.addHandler(console)
log.setLevel(logging.INFO)

def set_debug(onoff):
    if onoff:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)


class Zpi(Znp):
    """
        A class implements TI ZPI (ZNP API) functions
    """
    znp_commands = ZpiCommands.znp_commands
    znp_responses = ZpiCommands.znp_responses

    SRSP_WAITING_TIMEOUT_DEFAULT = 0.500 #SRSP wait timeout default value: 200ms

    def __init__(self, ser, callback = None):
        #this is an async callback
        self._async_callback = callback

        #init sync callback handlers list t empty
        self._srsp_handlers = []
        self._rx_msg_q = Queue.deque()  #rx_data queue
        self._areq_rx_msg = None
        self._srsp_rx_msg = None

        #init conditional vars
        self._areq_arrived = threading.Condition()
        self._srsp_arrived = threading.Condition()

        #init event vars
        self._is_areq_arrived = threading.Event()
        self._is_srsp_arrived = threading.Event()

        self._srsp_events = {}   #ZpiCommand:event, each SRSP holds an event

        #set to default callback for dispatcher
        super(Zpi, self).__init__(ser, self._callback_dispatcher)

    def _callback_dispatcher(self, rx_data):
        """
            This is intended to dispatch the responses from ZNP device shall be
            invoked in its own thread.
            Async responses will be filtered for self._async_callback handler.
            Sync response will be filtered and process by own handlers.
        """
        if rx_data is None:
            return

        for field_name, field_value in rx_data.iteritems():
            if field_name != 'id':
                log.debug('%s: %s' % (field_name, field_value.encode('hex')))


        #get rx_data id and find related registered handler if existed
        cmd0 = struct.unpack('<B', rx_data['cmd0'])[0]
        if (cmd0 >> 5) ==  ZnpFrame.CMD_SRSP:  #filter SRSP commands
            #put data and then set event
            self._srsp_rx_msg = rx_data
            self._srsp_event_set(rx_data['id'])

        elif (cmd0 >> 5) == ZnpFrame.CMD_AREQ: #filter AREQ commands
            if self._async_callback is not None:
                try:
                    self._async_callback(self, rx_data)
                except:
                    log.warning('async callback error: %s' %
                                self._async_callback.__name__)
                    raise
            else:
                self._areq_arrived.acquire()
                self._areq_rx_msg = rx_data
                self._areq_arrived.notify()
                self._areq_arrived.release()
                self._is_areq_arrived.set()
        else:
            log.debug('Not handled Rx response.')

    def _srsp_event_clear(self, zpi_cmd):
        """ clear the zpi_cmd event, ignore it if not existed """
        if zpi_cmd in self._srsp_events:
            self._srsp_events[zpi_cmd].clear()

    def _srsp_event_set(self, zpi_cmd):
        """ set zpi_cmd event, create the event if not existed """
        if zpi_cmd not in self._srsp_events:
            self._srsp_events[zpi_cmd] = threading.Event()

        self._srsp_events[zpi_cmd].set()

    def _srsp_event_wait(self, zpi_cmd, timeout = SRSP_WAITING_TIMEOUT_DEFAULT):
        """ wait the zpi_cmd event, immd. create one event it if not existed """
        if zpi_cmd not in self._srsp_events:
            self._srsp_events[zpi_cmd] = threading.Event()

        return self._srsp_events[zpi_cmd].wait(timeout)


    ############################################################################
    #system interface APIs
    ############################################################################
    def sys_reset_req(self, reset_type):
        """ reset the radio and wait for the reset indication """
        if ((reset_type != ResetType.HARD_RESET) and
            (reset_type != ResetType.SOFT_RESET)):
            raise ValueError('Invalid reset type: %s' % repr(reset_type))

        self.send(ZpiCommand.SYS_RESET_REQ, type = struct.pack('<B', reset_type))

    def sys_reset_ind_handler(self, rx_data):
        """ reset indication handler"""
        if rx_data['id'] == ZpiCommand.SYS_RESET_IND:
            reason = struct.unpack('<B', rx_data['reason'])[0]
            transport_rev = struct.unpack('<B', rx_data['transport_rev'])[0]
            product_id = struct.unpack('<B', rx_data['product_id'])[0]
            major_rel = struct.unpack('<B', rx_data['major_rel'])[0]
            minor_rel = struct.unpack('<B', rx_data['minor_rel'])[0]
            hw_rev = struct.unpack('<B', rx_data['hw_rev'])[0]

            return reason, transport_rev, product_id, major_rel, minor_rel, hw_rev
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.SYS_RESET_IND, rx_data['id']))

    def sys_version(self):
        """ request for the ZNP software version information """
        self._srsp_event_clear(ZpiCommand.SYS_VERSION_SRSP)
        self.send(ZpiCommand.SYS_VERSION)
        self._srsp_event_wait(ZpiCommand.SYS_VERSION_SRSP)

        return self._sys_version_srsp_handler(self._srsp_rx_msg)

    def _sys_version_srsp_handler(self, rx_data):
        """ handle system version srsp """
        if rx_data['id'] == ZpiCommand.SYS_VERSION_SRSP:
            transport_rev = struct.unpack('<B', rx_data['transport_rev'])[0]
            product_id = struct.unpack('<B', rx_data['product_id'])[0]
            major_rel = struct.unpack('<B', rx_data['major_rel'])[0]
            minor_rel = struct.unpack('<B', rx_data['minor_rel'])[0]
            maint_rel = struct.unpack('<B', rx_data['maint_rel'])[0]

            return transport_rev, product_id, major_rel, minor_rel, maint_rel
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.SYS_VERSION_SRSP, rx_data['id']))

    def sys_adc_read(self, channel, resolution):
        """ read on-chip ADC channel value """
        # pre-check channel range?
        self._srsp_event_clear(ZpiCommand.SYS_ADC_READ_SRSP)
        self.send(ZpiCommand.SYS_ADC_READ, channel = struct.pack('<B', channel),
                  resolution = struct.pack('<B', resolution))
        self._srsp_event_wait(ZpiCommand.SYS_ADC_READ_SRSP)

        return self._sys_adc_read_srsp_handler(self._srsp_rx_msg)

    def _sys_adc_read_srsp_handler(self, rx_data):
        """ handle system adc read srsp """
        if rx_data['id'] == ZpiCommand.SYS_ADC_READ_SRSP:
            return struct.unpack('<H', rx_data['value'])[0]
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.SYS_ADC_READ_SRSP, rx_data['id']))

    def sys_gpio(self, operation, value):
        """ configure the accessible GPIO pins on CC2530-ZNP device"""
        self._srsp_event_clear(ZpiCommand.SYS_GPIO_SRSP)
        self.send(ZpiCommand.SYS_GPIO, operation = struct.pack('<B', operation),
                  value = struct.pack('<B', value))
        self._srsp_event_wait(ZpiCommand.SYS_GPIO_SRSP)
        return self.sys_gpio_srsp_handler(self._srsp_rx_msg)

    def sys_gpio_srsp_handler(self, rx_data):
        """ handler for system GPIO srsp """
        if rx_data['id'] == ZpiCommand.SYS_GPIO_SRSP:
            return struct.unpack('<B', rx_data['value'])[0]
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.SYS_GPIO_SRSP, rx_data['id']))

    def sys_random(self):
        """ get a 16-bit random number """
        self._srsp_event_clear(ZpiCommand.SYS_RANDOM_SRSP)
        self.send(ZpiCommand.SYS_RANDOM)
        self._srsp_event_wait(ZpiCommand.SYS_RANDOM_SRSP)
        return self._sys_random_srsp_handler(self._srsp_rx_msg)

    def _sys_random_srsp_handler(self, rx_data):
        """ handler for system random srsp"""
        if rx_data['id'] == ZpiCommand.SYS_RANDOM_SRSP:
            return struct.unpack('<H', rx_data['value'])[0]
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.SYS_RANDOM_SRSP, rx_data['id']))

    def sys_set_time(self, time_set = None):
        """set the time of ZNP device """
        if time_set is not None:
            #get current OS date time
            dt = datetime.datetime.now()
        else:
            dt = time_set

        self.send(ZpiCommand.SYS_SET_TIME,
                  utc_time = struct.pack('<L', 0),      #not use UTC format
                  hour = struct.pack('<B', dt.hour),
                  minute = struct.pack('<B',dt.minute),
                  second = struct.pack('<B',dt.second),
                  month = struct.pack('<B',dt.month),
                  day = struct.pack('<B',dt.day),
                  year = struct.pack('<B',dt.year))

    def sys_set_time_srsp_handler(self, rx_data):
        """ handle system set time srsp"""
        if rx_data['id'] == ZpiCommand.SYS_SET_TIME_SRSP:
            status = struct.unpack('<B', rx_data['status'])[0]

            return status
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.SYS_SET_TIME_SRSP, rx_data['id']))

    def sys_get_time(self):
        """ get time from ZNP device """
        self.send(ZpiCommand.SYS_GET_TIME)

    def _sys_get_time_srsp_handler(self, rx_data):
        """ handler of system time get """
        if rx_data['id'] == ZpiCommand.SYS_GET_TIME_SRSP:
            #utc field is ignored
            hour = struct.unpack('<B', rx_data['hour'])[0]
            minute = struct.unpack('<B', rx_data['minute'])[0]
            second = struct.unpack('<B', rx_data['second'])[0]
            month = struct.unpack('<B', rx_data['month'])[0]
            day = struct.unpack('<B', rx_data['day'])[0]
            year = struct.unpack('<B', rx_data['year'])[0]

            time_get = datetime.datetime(year, month, day, hour, minute, second)
            return time_get
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.SYS_GET_TIME_SRSP, rx_data['id']))


    ############################################################################
    #CONFIG interface
    ############################################################################
    def zb_read_config(self, config_id):
        """ read configuration parameters from ZNP NV space
            return: (status, data)

        """
        if ((config_id in ConfigParameter.uint8_type) or
           (config_id in ConfigParameter.uint16_type) or
           (config_id in ConfigParameter.uint32_type) or
           (config_id in ConfigParameter.uint64_type) or
           (config_id in ConfigParameter.array_4bytes_type) or
           (config_id in ConfigParameter.array_16bytes_type) or
           (config_id in ConfigParameter.user_defined_type)):
            self._srsp_event_clear(ZpiCommand.ZB_READ_CONFIGURATION_SRSP)
            self.send(ZpiCommand.ZB_READ_CONFIGURATION,
                      config_id = struct.pack('<B', config_id))
            if self._srsp_event_wait(ZpiCommand.ZB_READ_CONFIGURATION_SRSP):
                return self._zb_read_config_srsp_handler(self._srsp_rx_msg)
            else:
                raise SrspTimeoutException()
        else:
            raise ValueError('Invalid Config ID: %s', config_id)

    def _zb_read_config_srsp_handler(self, rx_data):
        """ handler of zb read config srsp """
        if rx_data['id'] == ZpiCommand.ZB_READ_CONFIGURATION_SRSP:
            status = struct.unpack('<B', rx_data['status'])[0]
            config_id = struct.unpack('<B', rx_data['config_id'])[0]
            length = struct.unpack('<B', rx_data['len'])[0]
            value = rx_data['value']

            #data = None
            if config_id in ConfigParameter.uint8_type:
                #unpack UINT8
                data = struct.unpack('<B', value)[0]
            elif config_id in ConfigParameter.uint16_type:
                #unpack UINT16
                data = struct.unpack('<H', value)[0]
            elif config_id in ConfigParameter.uint32_type:
                #unpack UINT32
                data = struct.unpack('<L', value)[0]
            elif config_id in ConfigParameter.uint64_type:
                #unpack UINT64
                data = struct.unpack('<Q', value)[0]
            elif config_id in ConfigParameter.array_4bytes_type:
                #unpack 4 bytes array
                if length == 4:
                    data = value
                else:
                    raise ValueError('RF test params must be 4-bytes long!')
            elif config_id in ConfigParameter.array_16bytes_type:
                #unpack byte array : 16bytes
                if length == 16:
                    data = value
                else:
                    raise ValueError('Pre-configured key must be 16-bytes long!')
            elif config_id in ConfigParameter.user_defined_type:
                #unpack byte array
                data = value #struct.pack('S', value)  #length check?
            else:
                raise ValueError('Invalid Config ID: %s', config_id)

            return status, data#(status, config_id, data)
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZB_READ_CONFIGURATION_SRSP, rx_data['id']))


    def zb_write_config(self, config_id, value):
        """ write configuration parameters to ZNP NV space """
        #data_len = 0
        if config_id in ConfigParameter.uint8_type:
            #pack a byte
            data = struct.pack('<B', value)
            data_len = 1
        elif config_id in ConfigParameter.uint16_type:
            #pack UINT16
            data = struct.pack('<H', value)
            data_len = 2
        elif config_id in ConfigParameter.uint32_type:
            #pack UINT32
            data = struct.pack('<L', value)
            data_len = 4
        elif config_id in ConfigParameter.uint64_type:
            #pack UINT64
            data = struct.pack('<Q', value)
            data_len = 8
        elif config_id in ConfigParameter.array_4bytes_type:
            #pack 4 bytes array
            if len(value) == 4:
                data = value
                data_len = 4
            else:
                raise ValueError('RF test params must be 4-bytes long!')
        elif config_id in ConfigParameter.array_16bytes_type:
            #pack byte array : 16bytes
            if len(value) == 16:
                data = value
                data_len = 16
            else:
                raise ValueError('Pre-configured key must be 16-bytes long!')
        elif config_id in ConfigParameter.user_defined_type:
            #pack byte array
            data = value #struct.pack('S', value)  #length check?
            data_len = len(data)
        else:
            raise ValueError('Invalid Config ID: %s', config_id)

        self._srsp_event_clear(ZpiCommand.ZB_WRITE_CONFIGURATION_SRSP)
        self.send(ZpiCommand.ZB_WRITE_CONFIGURATION,
                  config_id = struct.pack('<B', config_id),
                  len = struct.pack('<B', data_len),
                  value = data)
        if self._srsp_event_wait(ZpiCommand.ZB_WRITE_CONFIGURATION_SRSP):
            return self._zb_write_config_srsp_handler(self._srsp_rx_msg)
        else:
            raise SrspTimeoutException()

    def _zb_write_config_srsp_handler(self, rx_data):
        """ handler of zb write config srsp """
        if rx_data['id'] == ZpiCommand.ZB_WRITE_CONFIGURATION_SRSP:
            status = struct.unpack('<B', rx_data['status'])[0]
            return  status
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZB_WRITE_CONFIGURATION_SRSP, rx_data['id']))

    ############################################################################
    #SAPI
    ############################################################################
    def zb_app_register_request(self, endpoint, profile_id, device_id, device_ver,
                                in_commands=None, out_commands=None):
        """
            register app on a specific endpoint. When SAPI used, only one
            endpoint could be registered.
        """
        if not out_commands: out_commands = []
        if not in_commands: in_commands = []
        in_cmd_list = b''
        for cmd in in_commands:
            in_cmd_list += struct.pack('<H', cmd)

        out_cmd_list = b''
        for cmd in out_commands:
            out_cmd_list += struct.pack('<H', cmd)

        self._srsp_event_clear(ZpiCommand.ZB_APP_REGISTER_REQUEST_SRSP)
        self.send(ZpiCommand.ZB_APP_REGISTER_REQUEST,
                  endpoint = struct.pack('<B', endpoint),
                  profile_id = struct.pack('<H', profile_id),
                  device_id = struct.pack('<H', device_id),
                  device_ver = struct.pack('<B', device_ver),
                  in_cmd_num = struct.pack('<B', len(in_commands)),
                  in_cmd_list = in_cmd_list,
                  out_cmd_num = struct.pack('<B', len(out_commands)),
                  out_cmd_list = out_cmd_list)
        self._srsp_event_wait(ZpiCommand.ZB_APP_REGISTER_REQUEST_SRSP)
        return self._zb_app_register_request_srsp_handler(self._srsp_rx_msg)

    def _zb_app_register_request_srsp_handler(self, rx_data):
        """ handler for zb app register srsp """
        if rx_data['id'] == ZpiCommand.ZB_APP_REGISTER_REQUEST_SRSP:
            return struct.unpack('<B', rx_data['status'])[0]
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZB_APP_REGISTER_REQUEST_SRSP, rx_data['id']))

    def zb_start_request(self):
        """ SAPI - Start ZNP device"""
        self.send(ZpiCommand.ZB_START_REQUEST)

        #need to lock self._srsp_rx_msg variable shared in 2 threads???
        while True:
            self._is_srsp_arrived.wait(Zpi.SRSP_WAITING_TIMEOUT_DEFAULT)

            if (self._srsp_rx_msg is not None and
               self._srsp_rx_msg['id'] == ZpiCommand.ZB_START_REQUEST_SRSP):
                rx_data = self._srsp_rx_msg
                self._is_srsp_arrived.clear()

                if rx_data is not None:
                    return self._zb_start_request_srsp_handler(rx_data)
                else:
                    raise AreqTimeoutException('Wait for %s timeout.' %
                                               ZpiCommand.ZB_START_REQUEST_SRSP)

    def _zb_start_request_srsp_handler(self, rx_data):
        """ handle the start reuqest srsp """
        if rx_data['id'] == ZpiCommand.ZB_START_REQUEST_SRSP:
            return
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZB_START_REQUEST_SRSP, rx_data['id']))

    def zb_start_confirm_areq_handler(self, rx_data):
        if rx_data['id'] == ZpiCommand.ZB_START_CONFIRM:
            return struct.unpack('<B', rx_data['status'])[0]
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZB_START_CONFIRM, rx_data['id']))

    def zb_permit_joining_request(self, dst_addr, timeout):
        """ send SAPI zb permit joining request"""
        self._srsp_event_clear(ZpiCommand.ZB_PERMIT_JOINING_REQUEST_SRSP)
        self.send(ZpiCommand.ZB_PERMIT_JOINING_REQUEST,
                  dst_addr = struct.pack('<H', dst_addr),
                  timeout = struct.pack('<B', timeout))
        if self._srsp_event_wait(ZpiCommand.ZB_PERMIT_JOINING_REQUEST_SRSP):
            return self._zb_permit_joinning_request_srsp_handler(self._srsp_rx_msg)
        else:
            raise SrspTimeoutException()

    def _zb_permit_joinning_request_srsp_handler(self, rx_data):
        """ handler of zb_permit_joining_request srsp """
        if rx_data['id'] == ZpiCommand.ZB_PERMIT_JOINING_REQUEST_SRSP:
            return struct.unpack('<B', rx_data['status'])[0]
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZB_PERMIT_JOINING_REQUEST_SRSP, rx_data['id']))

    def zb_bind_device(self, action, cmd_id, dst_addr_long = 0x0):
        """
            bind device to default src endpoint and dst endpoint
            dst_addr_long = 0 will make all device in AllowBind mode accept
        """
        if action not in (BindAction.DELETE_BIND, BindAction.CREATE_BIND):
            raise ValueError('Invalid action value: %s' % repr(action))

        self._srsp_event_clear(ZpiCommand.ZB_BIND_DEVICE_SRSP)

        self.send(ZpiCommand.ZB_BIND_DEVICE,
                  create = struct.pack('<B', action),
                  cmd_id = struct.pack('<H', cmd_id),
                  dst_addr_long = struct.pack('<Q', dst_addr_long))

        if self._srsp_event_wait(ZpiCommand.ZB_BIND_DEVICE_SRSP):
            return self._zb_bind_device_srsp_handler(self._srsp_rx_msg)
        else:
            raise SrspTimeoutException()

    def _zb_bind_device_srsp_handler(self, rx_data):
        """ SRSP handler for ZB_BIND_DEVICE """
        if rx_data['id'] == ZpiCommand.ZB_BIND_DEVICE_SRSP:
            return
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZB_BIND_DEVICE_SRSP, rx_data['id']))

    def zb_bind_confirm_handler(self, rx_data):
        """ default AREQ handler for ZB_BIND_CONFIRM """
        if rx_data['id'] == ZpiCommand.ZB_BIND_CONFIRM:
            cmd_id = struct.unpack('<H', rx_data['cmd_id'])[0]
            status = struct.unpack('<B', rx_data['status'])[0]
            return cmd_id, status
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZB_BIND_CONFIRM, rx_data['id']))

    def zb_allow_bind(self, timeout):
        """
            put the device in the Allowing Binding Mode for a given period of
            time.

            timeout:  number of seconds to remain in the allow binding mode.
                      range from 1~65.
                      0: disable allow binding mode.
                      >64: indefinitely allow binding
        """
        self._srsp_event_clear(ZpiCommand.ZB_ALLOW_BIND_SRSP)
        self.send(ZpiCommand.ZB_ALLOW_BIND,
                  timeout = struct.pack('<B', timeout))
        if self._srsp_event_wait(ZpiCommand.ZB_ALLOW_BIND_SRSP):
            return self._zb_allow_bind_srsp_handler(self._srsp_rx_msg)
        else:
            raise SrspTimeoutException('Wait for %s timeout.' %
                                       ZpiCommand.ZB_ALLOW_BIND_SRSP)

    def _zb_allow_bind_srsp_handler(self, rx_data):
        """ SRSP handler for ZB_ALLOW_BIND """
        if rx_data['id'] == ZpiCommand.ZB_ALLOW_BIND_SRSP:
            return
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZB_ALLOW_BIND_SRSP, rx_data['id']))

    def zb_allow_bind_confirm_handler(self, rx_data):
        """AREQ handler for ZB_ALLOW_BIND_CONFIRM """
        if rx_data['id'] == ZpiCommand.ZB_ALLOW_BIND_CONFIRM:
            return struct.unpack('<H', rx_data['source'])[0]
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZB_ALLOW_BIND_CONFIRM, rx_data['id']))

    #noinspection PyUnusedLocal
    def zb_send_data_request(self, dst_addr_short, cmd_id, handle, tx_options,
                             radius, payload = ''):
        """ send data to the default registered endpoint on dst device """
        self._srsp_event_clear(ZpiCommand.ZB_SEND_DATA_REQUEST_SRSP)
        self.send(ZpiCommand.ZB_SEND_DATA_REQUEST,
                  dst_addr_short = struct.pack('<H', dst_addr_short),
                  cmd_id = struct.pack('<H', cmd_id),
                  len = struct.pack('<B', len(payload)),
                  data = payload)
        if self._srsp_event_wait(ZpiCommand.ZB_SEND_DATA_REQUEST_SRSP):
            return self._zb_send_data_request_srsp_handler(self._srsp_rx_msg)
        else:
            raise SrspTimeoutException()

    def _zb_send_data_request_srsp_handler(self, rx_data):
        """ handler for ZB_SEND_DATA_REQUEST SRSP"""
        if rx_data['id'] == ZpiCommand.ZB_SEND_DATA_REQUEST_SRSP:
            return
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZB_SEND_DATA_REQUEST_SRSP, rx_data['id']))

    def zb_send_data_confirm_areq_handler(self, rx_data):
        if rx_data['id'] == ZpiCommand.ZB_SEND_DATA_CONFIRM:
            return (struct.unpack('<B', rx_data['handle'])[0],
                    struct.unpack('<B', rx_data['status'])[0])
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZB_SEND_DATA_CONFIRM, rx_data['id']))

    def zb_receive_data_indication_areq_handler(self, rx_data):
        if rx_data['id'] == ZpiCommand.ZB_RECEIVE_DATA_INDICATION:
            return (struct.unpack('<H', rx_data['src_addr'])[0],
                    struct.unpack('<H', rx_data['cmd'])[0],
                    struct.unpack('<H', rx_data['len'])[0],
                    rx_data['data'])
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZB_RECEIVE_DATA_INDICATION, rx_data['id']))

    def zb_get_device_info(self, param):
        """ get the device information """
        if param in DeviceInfoParameter.params_len:
            #first clear event before sending
            self._srsp_event_clear(ZpiCommand.ZB_GET_DEVICE_INFO_SRSP)
            self.send(ZpiCommand.ZB_GET_DEVICE_INFO,
                      param = struct.pack('<B', param))
            #use a little long timeout to avoid timeout exception
            if self._srsp_event_wait(ZpiCommand.ZB_GET_DEVICE_INFO_SRSP, timeout = 0.300):
                return self._zb_get_dvice_info_srsp_handler(self._srsp_rx_msg)
            else:
                raise SrspTimeoutException()

    def _zb_get_dvice_info_srsp_handler(self, rx_data):
        """ handle the get device info srsp """
        if rx_data['id'] == ZpiCommand.ZB_GET_DEVICE_INFO_SRSP:
            param = struct.unpack('<B', rx_data['param'])[0]
            value = None
            if param in DeviceInfoParameter.params_len:
                if DeviceInfoParameter.params_len[param] == 1:
                    value = struct.unpack('<B', rx_data['value'][0])[0]
                elif DeviceInfoParameter.params_len[param] == 2:
                    value = struct.unpack('<H', rx_data['value'][0:2])[0]
                elif DeviceInfoParameter.params_len[param] == 8:
                    value = struct.unpack('<Q', rx_data['value'])[0]
            else:
                raise ValueError('Invalid parameter id: %d' % param)

            return value
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZB_GET_DEVICE_INFO_SRSP, rx_data['id']))

    def zb_find_device_request(self, search_key):
        pass


    def _zb_find_device_request_srsp_handler(self, rx_data):
        pass

    def zb_find_device_confirm_areq_handler(self, rx_data):
        pass

    #AF interface
    def af_register(self, endpoint, profile_id, device_id, device_ver,
                    latency_req, in_clusters = None, out_clusters = None):
        """ register app on a given endpoint """
        if in_clusters is None:
            in_clusters = []
        in_cluster_list = b''
        for in_cluster in in_clusters:
            in_cluster_list += struct.pack('<H', in_cluster)

        if out_clusters is None:
            out_clusters = []
        out_cluster_list = b''
        for out_cluster in out_clusters:
            out_cluster_list += struct.pack('<H', out_cluster)

        self._srsp_event_clear(ZpiCommand.AF_REGISTER_SRSP)
        self.send(ZpiCommand.AF_REGISTER,
                  endpoint = struct.pack('<B', endpoint),
                  profile_id = struct.pack('<H', profile_id),
                  device_id = struct.pack('<H', device_id),
                  device_ver = struct.pack('<B', device_ver<<4),
                  latency_req = struct.pack('<B', latency_req),
                  in_cluster_num = struct.pack('<B', len(in_clusters)),
                  in_cluster_list = in_cluster_list,
                  out_cluster_num = struct.pack('<B', len(out_clusters)),
                  out_cluster_list = out_cluster_list)
        if self._srsp_event_wait(ZpiCommand.AF_REGISTER_SRSP):
            return self._af_register_srsp_handler(self._srsp_rx_msg)
        else:
            return SrspTimeoutException()

    def _af_register_srsp_handler(self, rx_data):
        """ handler of AF_REGISTER SRSP """
        if rx_data['id'] == ZpiCommand.AF_REGISTER_SRSP:
            return struct.unpack('<B', rx_data['status'])[0]
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.AF_REGISTER_SRSP, rx_data['id']))

    def af_data_request(self, dst_addr, dst_ep, src_ep, cluster_id, trans_id,
                        options, radius, data = None):
        """ send a message through AF layer """
        if data is None:
            data = b''

        self._srsp_event_clear(ZpiCommand.AF_DATA_REQUEST_SRSP)
        self.send(ZpiCommand.AF_DATA_REQUEST,
                  dst_addr = struct.pack('<H', dst_addr),
                  dst_ep = struct.pack('<B', dst_ep),
                  src_ep = struct.pack('<B', src_ep),
                  cluster_id = struct.pack('<H', cluster_id),
                  trans_id = struct.pack('<B', trans_id),
                  options = struct.pack('<B', options),
                  radius = struct.pack('<B', radius),
                  len = struct.pack('<B', len(data)),
                  data = data)
        if self._srsp_event_wait(ZpiCommand.AF_DATA_REQUEST_SRSP):
            return self._af_data_request_srsp_handler(self._srsp_rx_msg)
        else:
            raise SrspTimeoutException()

    def _af_data_request_srsp_handler(self, rx_data):
        """ handler of AF_DATA_REQUEST SRSP """
        if rx_data['id'] == ZpiCommand.AF_DATA_REQUEST_SRSP:
            return struct.unpack('<B', rx_data['status'])[0]
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.AF_DATA_REQUEST_SRSP, rx_data['id']))

    def af_data_request_ext(self, dst_addr_mode, dst_addr, dst_ep, dst_pan_id,
                            src_ep, cluster_id, trans_id, options, radius, data):
        """
            this extended form of AF_DATA_REQUEST could be used to send the
            following messages:
            - Inter-PAN message
            - Multi-cast message (group address specified)
            - Binding message
        """
        if data is None:
            data = b''

        self._srsp_event_clear(ZpiCommand.AF_DATA_REQUEST_EXT_SRSP)
        self.send(ZpiCommand.AF_DATA_REQUEST_EXT,
                  dst_addr_mode = struct.pack('<B', dst_addr_mode),
                  dst_addr = struct.pack('<Q', dst_addr),
                  dst_ep = struct.pack('<B', dst_ep),
                  dst_pan_id = struct.pack('<H', dst_pan_id),
                  src_ep = struct.pack('<B', src_ep),
                  cluster_id = struct.pack('<H', cluster_id),
                  trans_id = struct.pack('<B', trans_id),
                  options = struct.pack('<B', options),
                  radius = struct.pack('<B', radius),
                  len = struct.pack('<H', len(data)),
                  data = data)
        if self._srsp_event_wait(ZpiCommand.AF_DATA_REQUEST_EXT_SRSP):
            return self._af_data_request_ext_srsp_handler(self._srsp_rx_msg)
        else:
            raise SrspTimeoutException()

    def _af_data_request_ext_srsp_handler(self, rx_data):
        """ handler of AF_DATA_REQUEST_EXT SRSP """
        if rx_data['id'] == ZpiCommand.AF_DATA_REQUEST_EXT_SRSP:
            return struct.unpack('<B', rx_data['status'])[0]
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.AF_DATA_REQUEST_EXT_SRSP, rx_data['id']))

    def af_data_request_src_rtg(self, dst_addr, dst_ep, src_ep, cluster_id,
                                trans_id, options, radius, relays = None,
                                data = None):
        """ build and send a message through AF layer using source routing """
        if data is None:
            data = []

        if relays is None:
            relays = []
        relay_list = b''
        for relay in relays:
            relay_list += struct.pack('<H', relay)

        self._srsp_event_clear(ZpiCommand.AF_DATA_REQUEST_SRC_RTG_SRSP)
        self.send(ZpiCommand.AF_DATA_REQUEST_SRC_RTG,
                  dst_addr = struct.pack('<H', dst_addr),
                  dst_ep = struct.pack('<B', dst_ep),
                  src_ep = struct.pack('<B', src_ep),
                  cluster_id = struct.pack('<H', cluster_id),
                  trans_id = struct.pack('B', trans_id),
                  options = struct.pack('B', options),
                  radius = struct.pack('B', radius),
                  relay_cnt = struct.pack('B', len(relays)),
                  relay_list = relay_list,
                  len = struct.pack('B', len(data)),
                  data = data)
        if self._srsp_event_wait(ZpiCommand.AF_DATA_REQUEST_SRC_RTG_SRSP):
            return self._af_data_request_src_rtg_srsp_handler(self._srsp_rx_msg)
        else:
            raise SrspTimeoutException()

    def _af_data_request_src_rtg_srsp_handler(self, rx_data):
        if rx_data['id'] == ZpiCommand.AF_DATA_REQUEST_SRC_RTG_SRSP:
            return struct.unpack('<B', rx_data['status'])[0]
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.AF_DATA_REQUEST_SRC_RTG_SRSP, rx_data['id']))

    def af_inter_pan_ctl(self, command, data):
        """ INTER_PAN control """
        self._srsp_event_clear(ZpiCommand.AF_INTER_PAN_CTRL_SRSP)
        self.send(ZpiCommand.AF_INTER_PAN_CTRL,
                  command = struct.pack('<B', command),
                  data = InterPanCtlCommand.data_pack(command, data))
        if self._srsp_event_wait(ZpiCommand.AF_INTER_PAN_CTRL_SRSP):
            return self._af_inter_pan_ctl_srsp_handler(self._srsp_rx_msg)
        else:
            raise SrspTimeoutException()

    def _af_inter_pan_ctl_srsp_handler(self, rx_data):
        """ handler of AF_INTER_PAN_CTL SRSP """
        if rx_data['id'] == ZpiCommand.AF_INTER_PAN_CTRL_SRSP:
            return struct.unpack('<B', rx_data['status'])[0]
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.AF_INTER_PAN_CTRL_SRSP, rx_data['id']))

    def af_data_store(self, index, data = None):
        """
            this function is used to facilitate the transfer of large packets
            that use APS fragmentation for over-the-air transmission
        """
        if data is None:
            data = b''
        self._srsp_event_clear(ZpiCommand.AF_DATA_STORE_SRSP)
        self.send(ZpiCommand.AF_DATA_STORE,
                  index = struct.pack('<H', index),
                  len = struct.pack('<B', len(data)),
                  data = data)
        if self._srsp_event_wait(ZpiCommand.AF_DATA_STORE_SRSP):
            return self._af_data_store_srsp_handler(self._srsp_rx_msg)
        else:
            raise SrspTimeoutException()

    def _af_data_store_srsp_handler(self, rx_data):
        """ handler of AF_DATA_STORE SRSP """
        if rx_data['id'] == ZpiCommand.AF_DATA_STORE_SRSP:
            return struct.unpack('<B', rx_data['status'])[0]
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.AF_DATA_STORE_SRSP, rx_data['id']))

    def af_data_confirm_handler(self, rx_data):
        """default handler of AF_DATA_CONFRIM """
        if rx_data['id'] == ZpiCommand.AF_DATA_CONFIRM:
            status = struct.unpack('<B', rx_data['status'])[0]
            endpoint = struct.unpack('<B', rx_data['endpoint'])[0]
            trans_id = struct.unpack('<B', rx_data['trans_id'])[0]
            return status, endpoint, trans_id
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.AF_DATA_CONFIRM, rx_data['id']))


    def af_incoming_msg_handler(self, rx_data):
        """ handler of AF_INCOMING_MSG """
        if rx_data['id'] == ZpiCommand.AF_INCOMING_MSG:
            group_id = struct.unpack('<H', rx_data['group_id'])[0]
            cluster_id = struct.unpack('<H', rx_data['cluster_id'])[0]
            src_addr = struct.unpack('<H', rx_data['src_addr'])[0]
            src_ep = struct.unpack('<B', rx_data['src_ep'])[0]
            dst_ep = struct.unpack('<B', rx_data['dst_ep'])[0]
            was_broadcast = struct.unpack('<B', rx_data['was_broadcast'])[0]
            lqi = struct.unpack('<B', rx_data['lqi'])[0]
            security_use = struct.unpack('<B', rx_data['security_use'])[0]
            time_stamp = struct.unpack('<L', rx_data['time_stamp'])[0]
            trans_seq = struct.unpack('<B', rx_data['trans_seq'])[0]
            data_len = struct.unpack('<B', rx_data['len'])[0]
            data = rx_data['data']

            if data_len != len(data):
                raise ValueError('"len" field is not equal to length of data!')

            return (group_id, cluster_id, src_addr, src_ep, dst_ep, was_broadcast,
                    lqi, security_use, time_stamp, trans_seq, data)
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.AF_INCOMING_MSG, rx_data['id']))

    def af_incoming_msg_ext_handler(self, rx_data):
        """ handler of AF_INCOMING_MSG_EXT """
        if rx_data['id'] == ZpiCommand.AF_INCOMING_MSG_EXT:
            group_id = struct.unpack('<H', rx_data['group_id'])[0]
            cluster_id = struct.unpack('<H', rx_data['cluster_id'])[0]
            src_addr_mode = struct.unpack('<B', rx_data['src_addr_mode'])[0]
            src_addr = struct.unpack('<Q', rx_data['src_addr'])[0]
            src_ep = struct.unpack('<B', rx_data['src_ep'])[0]
            src_pan_id = struct.unpack('<H', rx_data['src_pan_id'])[0]
            dst_ep = struct.unpack('<B', rx_data['dst_ep'])[0]
            was_broadcast = struct.unpack('<B', rx_data['was_broadcast'])[0]
            lqi = struct.unpack('<B', rx_data['lqi'])[0]
            security_use = struct.unpack('<B', rx_data['security_use'])[0]
            time_stamp = struct.unpack('<L', rx_data['time_stamp'])[0]
            trans_seq = struct.unpack('<B', rx_data['trans_seq'])[0]
            data_len = struct.unpack('<B', rx_data['len'])[0]
            data = rx_data['data']

            if data_len != len(data):
                raise ValueError('"len" field is not equal to length of data!')

            return (group_id, cluster_id, src_addr_mode, src_addr, src_ep,
                    src_pan_id, dst_ep, was_broadcast, lqi, security_use,
                    time_stamp, trans_seq, data)
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.AF_INCOMING_MSG_EXT, rx_data['id']))

    def af_data_retrieve(self, time_stamp, index, length):
        """
            this function is used for receiving large packets that use APS
            fragmentation for over-the-air reception
        """
        self._srsp_event_clear(ZpiCommand.AF_DATA_RETRIEVE_SRSP)
        self.send(ZpiCommand.AF_DATA_RETRIEVE,
                  time_stamp = struct.pack('<L', time_stamp),
                  index = struct.pack('<H', index),
                  length = struct.pack('<B', length))
        if self._srsp_event_wait(ZpiCommand.AF_DATA_RETRIEVE_SRSP):
            return self._af_data_retrieve_srsp_handler(self._srsp_rx_msg)
        else:
            raise SrspTimeoutException()

    def _af_data_retrieve_srsp_handler(self, rx_data):
        """ handler of AF_DATA_RETRIEVE SRSP """
        if rx_data['id'] == ZpiCommand.AF_DATA_RETRIEVE_SRSP:
            return struct.unpack('<B', rx_data['status'])[0]
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.AF_DATA_RETRIEVE_SRSP, rx_data['id']))

    def af_apsf_config_set(self, endpoint, frame_delay, window_size):
        """
            change the default APS fragmentation configuration setting for a
            specific endpoint
        """
        self._srsp_event_clear(ZpiCommand.AF_APSF_CONFIG_SET_SRSP)
        self.send(ZpiCommand.AF_APSF_CONFIG_SET,
                  endpoint = struct.pack('<B', endpoint),
                  frame_delay = struct.pack('<B', frame_delay),
                  window_size = struct.pack('<B', window_size))
        if self._srsp_event_wait(ZpiCommand.AF_APSF_CONFIG_SET_SRSP):
            return self._af_apsf_config_set_srsp_handler(self._srsp_rx_msg)
        else:
            raise SrspTimeoutException()

    def _af_apsf_config_set_srsp_handler(self, rx_data):
        if rx_data['id'] == ZpiCommand.AF_APSF_CONFIG_SET_SRSP:
            return struct.unpack('<B', rx_data['status'])[0]
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.AF_APSF_CONFIG_SET_SRSP, rx_data['id']))

    #ZDO interface
    def zdo_nwk_addr_req(self, ieee_addr, req_type, start_index):
        """ request the device to send a Network Address Request. """
        self._srsp_event_clear(ZpiCommand.ZDO_NWK_ADDR_REQ_SRSP)
        self.send(ZpiCommand.ZDO_NWK_ADDR_REQ,
                  ieee_addr = struct.pack('<Q', ieee_addr),
                  req_type = struct.pack('<B', req_type),
                  start_index = struct.pack('<B', start_index))
        if self._srsp_event_wait(ZpiCommand.ZDO_NWK_ADDR_REQ_SRSP):
            return self._zdo_nwk_addr_req_srsp_handler(self._srsp_rx_msg)
        else:
            raise SrspTimeoutException()

    def _zdo_nwk_addr_req_srsp_handler(self, rx_data):
        """ handler of ZDO_NWK_ADDR_REQ SRSP """
        if rx_data['id'] == ZpiCommand.ZDO_NWK_ADDR_REQ_SRSP:
            return struct.unpack('<B', rx_data['status'])[0]
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZDO_NWK_ADDR_REQ_SRSP, rx_data['id']))

    def zdo_nwk_addr_rsp_handler(self, rx_data):
        """ default handler of ZDO_NWK_ADDR_RSP """
        if rx_data['id'] == ZpiCommand.ZDO_NWK_ADDR_RSP:
            status = struct.unpack('<B', rx_data['status'])[0]
            ieee_addr = struct.unpack('<Q', rx_data['ieee_addr'])[0]
            nwk_addr = struct.unpack('<H', rx_data['nwk_addr'])[0]
            start_index = struct.unpack('<B', rx_data['start_index'])[0]
            assoc_dev_num = struct.unpack('<B', rx_data['assoc_dev_num'])[0]
            assoc_dev_list = rx_data['assoc_dev_list']

            assoc_dev = []
            for assoc_dev_index in range(0, assoc_dev_num*2, 2):
                assoc_dev.append(struct.unpack('<H',
                    assoc_dev_list[assoc_dev_index:(assoc_dev_index + 2)])[0])

            return status, ieee_addr, nwk_addr, start_index, assoc_dev
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZDO_NWK_ADDR_RSP, rx_data['id']))

    def zdo_ieee_addr_req(self, nwk_addr, req_type = 0, start_index = 0):
        """ request the device to send a IEEE Address Request. """
        self._srsp_event_clear(ZpiCommand.ZDO_IEEE_ADDR_REQ_SRSP)
        self.send(ZpiCommand.ZDO_IEEE_ADDR_REQ,
                  nwk_addr = struct.pack('<H', nwk_addr),
                  req_type = struct.pack('<B', req_type),
                  start_index = struct.pack('<B', start_index))
        if self._srsp_event_wait(ZpiCommand.ZDO_IEEE_ADDR_REQ_SRSP, 0.500): #sometimes default value not enough
            return self._zdo_ieee_addr_req_srsp_handler(self._srsp_rx_msg)
        else:
            raise SrspTimeoutException()

    def _zdo_ieee_addr_req_srsp_handler(self, rx_data):
        """ handler of ZDO_IEEE_ADDR_REQ SRSP """
        if rx_data['id'] == ZpiCommand.ZDO_IEEE_ADDR_REQ_SRSP:
            return struct.unpack('<B', rx_data['status'])[0]
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZDO_IEEE_ADDR_REQ_SRSP, rx_data['id']))

    def zdo_ieee_addr_rsp_handler(self, rx_data):
        if rx_data['id'] == ZpiCommand.ZDO_IEEE_ADDR_RSP:
            status = struct.unpack('<B', rx_data['status'])[0]
            ieee_addr = struct.unpack('<Q', rx_data['ieee_addr'])[0]
            nwk_addr = struct.unpack('<H', rx_data['nwk_addr'])[0]
            start_index = struct.unpack('<B', rx_data['start_index'])[0]
            assoc_dev_num = struct.unpack('<B', rx_data['assoc_dev_num'])[0]

            assoc_dev = []
            if (assoc_dev_num != 0) and 'assoc_dev_list' in rx_data:
                assoc_dev_list = rx_data['assoc_dev_list']
                #assoc_dev_num is the total num of devices in entire list
                #assoc_dev_list returned here may be a partial list

                for assoc_dev_index in range(0, len(assoc_dev_list), 2):
                    assoc_dev.append(struct.unpack('<H',
                        assoc_dev_list[assoc_dev_index:(assoc_dev_index + 2)])[0])

            return status, ieee_addr, nwk_addr, start_index, assoc_dev_num, assoc_dev
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZDO_IEEE_ADDR_RSP, rx_data['id']))

    def zdo_node_desc_req(self, dst_addr, nwk_addr_of_interest):
        """
            inquire about the Node Descriptor information of the destination
            device.
        """
        self._srsp_event_clear(ZpiCommand.ZDO_NODE_DESC_REQ_SRSP)
        self.send(ZpiCommand.ZDO_NODE_DESC_REQ,
                  dst_addr = struct.pack('<H', dst_addr),
                  nwk_addr_of_interest = struct.pack('<H', nwk_addr_of_interest))
        if self._srsp_event_wait(ZpiCommand.ZDO_NODE_DESC_REQ_SRSP):
            return self._zdo_node_desc_req_srsp_handler(self._srsp_rx_msg)
        else:
            raise SrspTimeoutException()

    def _zdo_node_desc_req_srsp_handler(self, rx_data):
        """ handler of ZDO_NODE_DESC_REQ SRSP """
        if rx_data['id'] == ZpiCommand.ZDO_NODE_DESC_REQ_SRSP:
            return struct.unpack('<B', rx_data['status'])[0]
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZDO_NODE_DESC_REQ_SRSP, rx_data['id']))

    def zdo_node_desc_rsp_handler(self, rx_data):
        """ handler of ZDO_NODE_DESC_RSP """
        if rx_data['id'] == ZpiCommand.ZDO_NODE_DESC_RSP:
            src_addr = struct.unpack('<H', rx_data['src_addr'])[0]
            status = struct.unpack('<B', rx_data['status'])[0]
            nwk_addr = struct.unpack('<H', rx_data['nwk_addr'])[0]
            logical_type_flags = struct.unpack('<B', rx_data['logical_type_flags'])[0]
            aps_flags = struct.unpack('<B', rx_data['aps_flags'])[0]
            mac_cap_flags = struct.unpack('<B', rx_data['mac_cap_flags'])[0]
            mnfr_code = struct.unpack('<H', rx_data['mnfr_code'])[0]
            max_buf_size = struct.unpack('<B', rx_data['max_buf_size'])[0]
            max_trans_size = struct.unpack('<H', rx_data['max_trans_size'])[0]
            server_mask = struct.unpack('<H', rx_data['server_mask'])[0]
            max_out_trans_size = struct.unpack('<H', rx_data['max_out_trans_size'])[0]
            descriptor_cap = struct.unpack('<B', rx_data['descriptor_cap'])[0]

            return (src_addr, status, nwk_addr, logical_type_flags, aps_flags,
                    mac_cap_flags, mnfr_code, max_buf_size, max_trans_size,
                    server_mask, max_out_trans_size, descriptor_cap)
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZDO_NODE_DESC_RSP, rx_data['id']))


    def zdo_power_desc_req(self, dst_addr, nwk_addr_of_interest):
        """
            inquire about the Power Descriptor information of the destination
            device.
        """
        self._srsp_event_clear(ZpiCommand.ZDO_POWER_DESC_REQ_SRSP)
        self.send(ZpiCommand.ZDO_POWER_DESC_REQ,
                  dst_addr = struct.pack('<H', dst_addr),
                  nwk_addr_of_interest = struct.pack('<H', nwk_addr_of_interest))
        if self._srsp_event_wait(ZpiCommand.ZDO_POWER_DESC_REQ_SRSP):
            return self._zdo_power_desc_req_srsp_handler(self._srsp_rx_msg)
        else:
            raise SrspTimeoutException()

    def _zdo_power_desc_req_srsp_handler(self, rx_data):
        """ handler of ZDO_NODE_DESC_REQ SRSP """
        if rx_data['id'] == ZpiCommand.ZDO_POWER_DESC_REQ_SRSP:
            return struct.unpack('<B', rx_data['status'])[0]
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZDO_POWER_DESC_REQ_SRSP, rx_data['id']))

    def zdo_power_desc_rsp_handler(self, rx_data):
        if rx_data['id'] == ZpiCommand.ZDO_POWER_DESC_RSP:
            src_addr = struct.unpack('<H', rx_data['src_addr'])[0]
            status = struct.unpack('<B', rx_data['status'])[0]
            nwk_addr = struct.unpack('<H', rx_data['nwk_addr'])[0]
            cur_pwrmode_avail_pwrsrc = struct.unpack('<B', rx_data['cur_pwrmode_avail_pwrsrc'])[0]
            cur_pwrsrc_and_level = struct.unpack('<B', rx_data['cur_pwrsrc_and_level'])[0]

            return (src_addr, status, nwk_addr, cur_pwrmode_avail_pwrsrc,
                    cur_pwrsrc_and_level)
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZDO_POWER_DESC_RSP, rx_data['id']))

    def zdo_simple_desc_req(self, dst_addr, nwk_addr_of_interest, endpoint):
        """
            inquire about the Simple Descriptor information of the destination
            device's endpoint
        """
        self._srsp_event_clear(ZpiCommand.ZDO_SIMPLE_DESC_REQ_SRSP)
        self.send(ZpiCommand.ZDO_SIMPLE_DESC_REQ,
                  dst_addr = struct.pack('<H', dst_addr),
                  nwk_addr_of_interest = struct.pack('<H', nwk_addr_of_interest),
                  endpoint = struct.pack('<B', endpoint))
        if self._srsp_event_wait(ZpiCommand.ZDO_SIMPLE_DESC_REQ_SRSP, 1.0):
            return self._zdo_simple_desc_req_srsp_handler(self._srsp_rx_msg)
        else:
            raise SrspTimeoutException()

    def _zdo_simple_desc_req_srsp_handler(self, rx_data):
        """ handler of ZDO_SIMPLE_DESC_REQ SRSP """
        if rx_data['id'] == ZpiCommand.ZDO_SIMPLE_DESC_REQ_SRSP:
            return struct.unpack('<B', rx_data['status'])[0]
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZDO_SIMPLE_DESC_REQ_SRSP, rx_data['id']))

    def zdo_simple_desc_rsp_handler(self, rx_data):
        if rx_data['id'] == ZpiCommand.ZDO_SIMPLE_DESC_RSP:
            src_addr = struct.unpack('<H', rx_data['src_addr'])[0]
            status = struct.unpack('<B', rx_data['status'])[0]
            nwk_addr = struct.unpack('<H', rx_data['nwk_addr'])[0]
            length = struct.unpack('<B', rx_data['len'])[0]
            endpoint = struct.unpack('<B', rx_data['endpoint'])[0]
            profile_id = struct.unpack('<H', rx_data['profile_id'])[0]
            device_id = struct.unpack('<H', rx_data['device_id'])[0]
            device_ver = struct.unpack('<B', rx_data['device_ver'])[0] >> 4
            in_cluster_num = struct.unpack('<B', rx_data['in_cluster_num'])[0]
            in_clusters = []
            if in_cluster_num > 0:
                in_cluster_list = rx_data['in_cluster_list']
                #parsing clusters details
                for in_cluster_index in range(0, in_cluster_num*2, 2):
                    in_clusters.append(struct.unpack('<H',
                        in_cluster_list[in_cluster_index:(in_cluster_index + 2)])[0])

            out_cluster_num = struct.unpack('<B', rx_data['out_cluster_num'])[0]

            out_clusters = []
            if out_cluster_num > 0:
                out_cluster_list = rx_data['out_cluster_list']
                for out_cluster_index in range(0, out_cluster_num*2, 2):
                    out_clusters.append(struct.unpack('<H',
                        out_cluster_list[out_cluster_index:(out_cluster_index + 2)])[0])

            return (src_addr, status, nwk_addr, length, endpoint, profile_id,
                    device_id, device_ver, in_clusters, out_clusters)
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZDO_SIMPLE_DESC_RSP, rx_data['id']))

    def zdo_active_ep_req(self, dst_addr, nwk_addr_of_interest):
        """
            request a list of active endpoints from the destination device.
        """
        self._srsp_event_clear(ZpiCommand.ZDO_ACTIVE_EP_REQ_SRSP)
        self.send(ZpiCommand.ZDO_ACTIVE_EP_REQ,
                  dst_addr = struct.pack('<H', dst_addr),
                  nwk_addr_of_interest = struct.pack('<H', nwk_addr_of_interest))
        if self._srsp_event_wait(ZpiCommand.ZDO_ACTIVE_EP_REQ_SRSP):
            return self._zdo_active_ep_req_srsp_handler(self._srsp_rx_msg)
        else:
            raise SrspTimeoutException()

    def _zdo_active_ep_req_srsp_handler(self, rx_data):
        """ handler of ZDO_ACTIVE_EP_REQ SRSP """
        if rx_data['id'] == ZpiCommand.ZDO_ACTIVE_EP_REQ_SRSP:
            return struct.unpack('<B', rx_data['status'])[0]
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZDO_ACTIVE_EP_REQ_SRSP, rx_data['id']))

    def zdo_active_ep_rsp_handler(self, rx_data):
        if rx_data['id'] == ZpiCommand.ZDO_ACTIVE_EP_RSP:
            src_addr = struct.unpack('<H', rx_data['src_addr'])[0]
            status = struct.unpack('<B', rx_data['status'])[0]
            nwk_addr =  struct.unpack('<H', rx_data['nwk_addr'])[0]
            active_ep_cnt = struct.unpack('<B', rx_data['active_ep_cnt'])[0]
            active_eps = []
            if active_ep_cnt > 0:
                active_ep_list = rx_data['active_ep_list']

                for active_ep_index in range(0, active_ep_cnt):
                    active_eps.append(struct.unpack('<B',
                                                    active_ep_list[active_ep_index: (active_ep_index + 1)])[0])

            return src_addr, status, nwk_addr, active_eps
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZDO_ACTIVE_EP_RSP, rx_data['id']))

    def zdo_match_desc_req(self, dst_addr, nwk_addr_of_interest, profile_id,
                           in_clusters = None, out_clusters = None):
        """
            send a match descriptor request, which is used to find devices that
            match the given criteria.
        """
        if in_clusters is None:
            in_clusters = []
        in_cluster_list = b''
        for in_cluster in in_clusters:
            in_cluster_list += struct.pack('<H', in_cluster)

        if out_clusters is None:
            out_clusters = []
        out_cluster_list = b''
        for out_cluster in out_clusters:
            out_cluster_list += struct.pack('<H', out_cluster)

        self._srsp_event_clear(ZpiCommand.ZDO_MATCH_DESC_REQ_SRSP)
        self.send(ZpiCommand.ZDO_MATCH_DESC_REQ,
                  dst_addr = struct.pack('<H', dst_addr),
                  nwk_addr_of_interest = struct.pack('<H', nwk_addr_of_interest),
                  profile_id = struct.pack('<H', profile_id),
                  in_cluster_num = struct.pack('<B', len(in_clusters)),
                  in_cluster_list = in_cluster_list,
                  out_cluster_num = struct.pack('<B', len(out_clusters)),
                  out_cluster_list = out_cluster_list)
        if self._srsp_event_wait(ZpiCommand.ZDO_MATCH_DESC_REQ_SRSP):
            return self._zdo_match_desc_req_srsp_handler(self._srsp_rx_msg)
        else:
            raise SrspTimeoutException()

    def _zdo_match_desc_req_srsp_handler(self, rx_data):
        """ handler of ZDO_ACTIVE_EP_REQ SRSP """
        if rx_data['id'] == ZpiCommand.ZDO_MATCH_DESC_REQ_SRSP:
            return struct.unpack('<B', rx_data['status'])[0]
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZDO_MATCH_DESC_REQ_SRSP, rx_data['id']))

    def zdo_match_desc_rsp_handler(self, rx_data):
        if rx_data['id'] == ZpiCommand.ZDO_MATCH_DESC_RSP:
            src_addr = struct.unpack('<H', rx_data['src_addr'])[0]
            status = struct.unpack('<B', rx_data['status'])[0]
            nwk_addr =  struct.unpack('<H', rx_data['nwk_addr'])[0]
            match_len = struct.unpack('<H', rx_data['match_len'])[0]
            match_list = rx_data['match_list']

            match_eps = []
            for match_index in range(0, match_len):
                match_eps.append(struct.unpack('<B',
                    match_list[match_index:(match_index + 1)])[0])

            return src_addr, status, nwk_addr, match_eps
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZDO_MATCH_DESC_RSP, rx_data['id']))

    def zdo_match_desc_rsp_sent_handler(self, rx_data):
        if rx_data['id'] == ZpiCommand.ZDO_MATCH_DESC_RSP_SENT:
            nwk_addr =  struct.unpack('<H', rx_data['nwk_addr'])[0]
            in_cluster_num = struct.unpack('<B', rx_data['in_cluster_num'])[0]
            if in_cluster_num > 0:
                in_cluster_list = rx_data['in_cluster_list']
            else:
                in_cluster_list = b''

            out_cluster_num = struct.unpack('<B', rx_data['out_cluster_num'])[0]

            if out_cluster_num > 0:
                out_cluster_list = rx_data['out_cluster_list']
            else:
                out_cluster_list = b''

            #parsing clusters details
            in_clusters = []
            for in_cluster_index in range(0, in_cluster_num*2, 2):
                in_clusters.append(struct.unpack('<H',
                    in_cluster_list[in_cluster_index:(in_cluster_index + 2)])[0])

            out_clusters = []
            for out_cluster_index in range(0, out_cluster_num*2, 2):
                out_clusters.append(struct.unpack('<H',
                    out_cluster_list[out_cluster_index:(out_cluster_index + 2)])[0])

            return nwk_addr, in_clusters, out_clusters
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZDO_MATCH_DESC_RSP_SENT, rx_data['id']))

    def zdo_complex_desc_req(self, dst_addr, nwk_addr_of_interest):
        """ request the destination device's complex descriptor """
        self._srsp_event_clear(ZpiCommand.ZDO_COMPLEX_DESC_REQ_SRSP)
        self.send(ZpiCommand.ZDO_COMPLEX_DESC_REQ,
                  dst_addr = struct.pack('<H', dst_addr),
                  nwk_addr_of_interest = struct.pack('<H', nwk_addr_of_interest))
        if self._srsp_event_wait(ZpiCommand.ZDO_COMPLEX_DESC_REQ_SRSP):
            return self._zdo_complex_desc_req_srsp_handler(self._srsp_rx_msg)
        else:
            raise SrspTimeoutException()

    def _zdo_complex_desc_req_srsp_handler(self, rx_data):
        """ handler of ZDO_COMPLEX_DESC_REQ  SRSP """
        if rx_data['id'] == ZpiCommand.ZDO_COMPLEX_DESC_REQ_SRSP:
            return struct.unpack('<B', rx_data['status'])[0]
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZDO_COMPLEX_DESC_REQ_SRSP, rx_data['id']))

    def zdo_complex_desc_rsp_handler(self, rx_data):
        if rx_data['id'] == ZpiCommand.ZDO_COMPLEX_DESC_RSP:
            src_addr = struct.unpack('<H', rx_data['src_addr'])[0]
            status = struct.unpack('<B', rx_data['status'])[0]
            nwk_addr =  struct.unpack('<H', rx_data['nwk_addr'])[0]
            complex_len = struct.unpack('<B', rx_data['complex_len'])[0]
            if complex_len > 0:
                complex_list = rx_data['complex_list']  #include XML tagged string
            else:
                complex_list = None

            return src_addr, status, nwk_addr, complex_len, complex_list
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZDO_COMPLEX_DESC_RSP, rx_data['id']))

    def zdo_user_desc_req(self, dst_addr, nwk_addr_of_interest):
        self._srsp_event_clear(ZpiCommand.ZDO_USER_DESC_REQ_SRSP)
        self.send(ZpiCommand.ZDO_USER_DESC_REQ,
                  dst_addr = struct.pack('<H', dst_addr),
                  nwk_addr_of_interest = struct.pack('<H', nwk_addr_of_interest))
        if self._srsp_event_wait(ZpiCommand.ZDO_USER_DESC_REQ_SRSP):
            return self._zdo_user_desc_req_srsp_handler(self._srsp_rx_msg)
        else:
            raise SrspTimeoutException()

    def _zdo_user_desc_req_srsp_handler(self, rx_data):
        """ handler of ZDO_ACTIVE_EP_REQ SRSP """
        if rx_data['id'] == ZpiCommand.ZDO_USER_DESC_REQ_SRSP:
            return struct.unpack('<B', rx_data['status'])[0]
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZDO_USER_DESC_REQ_SRSP, rx_data['id']))

    def zdo_user_desc_rsp_handler(self, rx_data):
        if rx_data['id'] == ZpiCommand.ZDO_USER_DESC_RSP:
            src_addr = struct.unpack('<H', rx_data['src_addr'])[0]
            status = struct.unpack('<B', rx_data['status'])[0]
            nwk_addr = struct.unpack('<H', rx_data['nwk_addr'])[0]
            length = struct.unpack('<B', rx_data['len'])[0]  #not returned
            if length > 0 and 'user_descriptor' in rx_data:
                user_descriptor = rx_data['user_descriptor']
            else:
                user_descriptor = None
            #check length with user_descriptor???
            return src_addr, status, nwk_addr, length, user_descriptor
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZDO_USER_DESC_RSP, rx_data['id']))

    def zdo_user_desc_confirm_handler(self, rx_data):
        if rx_data['id'] == ZpiCommand.ZDO_USER_DESC_CONF:
            src_addr = struct.unpack('<H', rx_data['src_addr'])[0]
            status = struct.unpack('<B', rx_data['status'])[0]
            nwk_addr = struct.unpack('<H', rx_data['nwk_addr'])[0]
            return src_addr, status, nwk_addr
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZDO_USER_DESC_CONF, rx_data['id']))

    def zdo_device_annce(self, nwk_addr, ieee_addr, capabilities):
        """
            request the ZNP device to issue a Devive Announce broadcast packet
            to the network
        """
        self._srsp_event_clear(ZpiCommand.ZDO_DEVICE_ANNCE_SRSP)
        self.send(ZpiCommand.ZDO_DEVICE_ANNCE,
                  nwk_addr = struct.pack('<H', nwk_addr),
                  ieee_addr = struct.pack('<H', ieee_addr),
                  capabilities = struct.pack('<B', capabilities))
        if self._srsp_event_wait(ZpiCommand.ZDO_DEVICE_ANNCE_SRSP):
            return self._zdo_device_annce_srsp_handler(self._srsp_rx_msg)
        else:
            raise SrspTimeoutException()

    def _zdo_device_annce_srsp_handler(self, rx_data):
        """ handler of ZDO_ACTIVE_EP_REQ SRSP """
        if rx_data['id'] == ZpiCommand.ZDO_DEVICE_ANNCE_SRSP:
            return struct.unpack('<B', rx_data['status'])[0]
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZDO_DEVICE_ANNCE_SRSP, rx_data['id']))

    def zdo_user_desc_set(self, dst_addr, nwk_addr_of_interest, user_descriptor):
        """ write a User Descriptor value to the target device """
        self._srsp_event_clear(ZpiCommand.ZDO_USER_DESC_SET_SRSP)
        self.send(ZpiCommand.ZDO_USER_DESC_SET,
                  dst_addr = struct.pack('<H', dst_addr),
                  nwk_addr_of_interest = struct.pack('<H', nwk_addr_of_interest),
                  len = struct.pack('<B', len(user_descriptor)),
                  user_descriptor = user_descriptor)
        if self._srsp_event_wait(ZpiCommand.ZDO_USER_DESC_SET_SRSP):
            return self._zdo_user_desc_set_srsp_handler(self._srsp_rx_msg)
        else:
            raise SrspTimeoutException()

    def _zdo_user_desc_set_srsp_handler(self, rx_data):
        """ handler of ZDO_USER_DESC_SET SRSP """
        if rx_data['id'] == ZpiCommand.ZDO_USER_DESC_SET_SRSP:
            return struct.unpack('<B', rx_data['status'])[0]
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZDO_USER_DESC_SET_SRSP, rx_data['id']))

    def zdo_server_disc_req(self, server_mask):
        """
            discover the location of a particular system server pr servers as
            indicated by server_mask parameter. The destination addressing on
            this request is broadcasted to all RxOnWhenIdle devices.
        """
        self._srsp_event_clear(ZpiCommand.ZDO_SERVER_DESC_REQ_SRSP)
        self.send(ZpiCommand.ZDO_SERVER_DESC_REQ,
                  server_mask=struct.pack('<H', server_mask))
        if self._srsp_event_wait(ZpiCommand.ZDO_SERVER_DESC_REQ_SRSP):
            return self._zdo_server_disc_req_srsp_handler(self._srsp_rx_msg)
        else:
            raise SrspTimeoutException()

    def _zdo_server_disc_req_srsp_handler(self, rx_data):
        """ handler of ZDO_SERVER_DISC_REQ SRSP """
        if rx_data['id'] == ZpiCommand.ZDO_SERVER_DESC_REQ_SRSP:
            return struct.unpack('<B', rx_data['status'])[0]
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZDO_SERVER_DESC_REQ_SRSP, rx_data['id']))

    def zdo_server_desc_rsp_handler(self, rx_data):
        if rx_data['id'] == ZpiCommand.ZDO_SERVER_DESC_RSP:
            src_addr = struct.unpack('<H', rx_data['src_addr'])[0]
            status = struct.unpack('<B', rx_data['status'])[0]
            server_mask = struct.unpack('<H', rx_data['server_mask'])[0]
            return src_addr, status, server_mask
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZDO_SERVER_DESC_RSP, rx_data['id']))

    def zdo_end_device_bind_req(self, dst_addr, local_coordinator,
                                local_coordinator_ieee_addr, endpoint,
                                profile_id, in_clusters, out_clusters):
        """ request an End Device Bind with the destination deivce """
        if in_clusters is None:
            in_clusters = []
        in_cluster_list = b''
        for in_cluster in in_clusters:
            in_cluster_list += struct.pack('<H', in_cluster)

        if out_clusters is None:
            out_clusters = []
        out_cluster_list = b''
        for out_cluster in out_clusters:
            out_cluster_list += struct.pack('<H', out_cluster)

        self._srsp_event_clear(ZpiCommand.ZDO_END_DEVICE_BIND_REQ_SRSP)
        self.send(ZpiCommand.ZDO_END_DEVICE_BIND_REQ,
                  dst_addr = struct.pack('<H', dst_addr),
                  local_coordinator = struct.pack('<H', local_coordinator),
                  ieee = struct.pack('<Q', local_coordinator_ieee_addr),
                  endpoint = struct.pack('<B', endpoint),
                  profile_id = struct.pack('<H', profile_id),
                  in_cluster_num = struct.pack('<B', len(in_clusters)),
                  in_cluster_list = in_cluster_list,
                  out_cluster_num = struct.pack('<B', len(out_clusters)),
                  out_cluster_list = out_cluster_list)
        if self._srsp_event_wait(ZpiCommand.ZDO_END_DEVICE_BIND_REQ_SRSP):
            return self._zdo_end_device_bind_req_srsp_handler(self._srsp_rx_msg)
        else:
            raise SrspTimeoutException()

    def _zdo_end_device_bind_req_srsp_handler(self, rx_data):
        """ handler of ZDO_END_DEVICE_BIND_REQ SRSP """
        if rx_data['id'] == ZpiCommand.ZDO_END_DEVICE_BIND_REQ_SRSP:
            return struct.unpack('<B', rx_data['status'])[0]
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZDO_END_DEVICE_BIND_REQ_SRSP, rx_data['id']))

    def zdo_end_device_bind_rsp_handler(self, rx_data):
        if rx_data['id'] == ZpiCommand.ZDO_END_DEVICE_BIND_RSP:
            src_addr = struct.unpack('<H', rx_data['src_addr'])[0]
            status = struct.unpack('<B', rx_data['status'])[0]
            return src_addr, status
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZDO_END_DEVICE_BIND_RSP, rx_data['id']))

    def zdo_bind_req(self, dst_addr, src_addr, src_ep, cluster_id,
                     bind_addr_mode, bind_addr, bind_ep):
        """ request a bind """
        self._srsp_event_elear(ZpiCommand.ZDO_BIND_REQ_SRSP)
        self.send(ZpiCommand.ZDO_BIND_REQ,
                  dst_addr = struct.pack('<H', dst_addr),
                  src_addr = struct.pack('<Q', src_addr),
                  src_ep = struct.pack('<B', src_ep),
                  cluster_id = struct.pack('<H', cluster_id),
                  bind_addr_mode = struct.pack('<H', bind_addr_mode),
                  bind_addr = struct.pack('<Q', bind_addr),
                  bind_ep = struct.pack('<B', bind_ep))
        if self._srsp_event_wait(ZpiCommand.ZDO_BIND_REQ_SRSP):
            return self._zdo_bind_req_srsp_handler(self._srsp_rx_msg)
        else:
            raise SrspTimeoutException()

    def _zdo_bind_req_srsp_handler(self, rx_data):
        """ handler of ZDO_END_DEVICE_BIND_REQ SRSP """
        if rx_data['id'] == ZpiCommand.ZDO_BIND_REQ_SRSP:
            return struct.unpack('<B', rx_data['status'])[0]
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZDO_BIND_REQ_SRSP, rx_data['id']))

    def zdo_bind_rsp_handler(self, rx_data):
        if rx_data['id'] == ZpiCommand.ZDO_BIND_RSP:
            src_addr = struct.unpack('<H', rx_data['src_addr'])[0]
            status = struct.unpack('<B', rx_data['status'])[0]
            return src_addr, status
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZDO_BIND_RSP, rx_data['id']))

    def zdo_unbind_req(self, dst_addr, src_addr, src_ep, cluster_id,
                       bind_addr_mode, bind_addr,bind_ep ):
        """ request a Unbind """
        self._srsp_event_clear(ZpiCommand.ZDO_UNBIND_REQ_SRSP)
        self.send(ZpiCommand.ZDO_UNBIND_REQ,
                  dst_addr = struct.pack('<H', dst_addr),
                  src_addr = struct.pack('<Q', src_addr),
                  src_ep = struct.pack('<B', src_ep),
                  cluster_id = struct.pack('<H', cluster_id),
                  bind_addr_mode = struct.pack('<H', bind_addr_mode),
                  bind_addr = struct.pack('<Q', bind_addr),
                  bind_ep = struct.pack('<B', bind_ep))
        if self._srsp_event_wait(ZpiCommand.ZDO_UNBIND_REQ_SRSP):
            return self._zdo_unbind_req_srsp_handler(self._srsp_rx_msg)
        else:
            raise SrspTimeoutException()

    def _zdo_unbind_req_srsp_handler(self, rx_data):
        """ handler of ZDO_UNBIND_REQ SRSP """
        if rx_data['id'] == ZpiCommand.ZDO_UNBIND_REQ_SRSP:
            return struct.unpack('<B', rx_data['status'])[0]
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZDO_UNBIND_REQ_SRSP, rx_data['id']))

    def zdo_unbind_rsp_handler(self, rx_data):
        if rx_data['id'] == ZpiCommand.ZDO_UNBIND_RSP:
            src_addr = struct.unpack('<H', rx_data['src_addr'])[0]
            status = struct.unpack('<B', rx_data['status'])[0]
            return src_addr, status
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZDO_UNBIND_RSP, rx_data['id']))

    def zdo_mgmt_nwk_disc_req(self, dst_addr, scan_channels, scan_duration,
                              start_index):
        """ request the destination device to perform a network discovery """
        self._srsp_event_clear(ZpiCommand.ZDO_MGMT_NWK_DISC_REQ_SRSP)
        self.send(ZpiCommand.ZDO_MGMT_NWK_DISC_REQ,
                  dst_addr = struct.pack('<H', dst_addr),
                  scan_channels = struct.pack('<L', scan_channels),
                  scan_duration = struct.pack('<B', scan_duration),
                  start_index = struct.pack('<B', start_index))
        if self._srsp_event_wait(ZpiCommand.ZDO_MGMT_NWK_DISC_REQ_SRSP):
            return self._zdo_mgmt_nwk_disc_req_srsp_handler(self._srsp_rx_msg)
        else:
            raise SrspTimeoutException()

    def _zdo_mgmt_nwk_disc_req_srsp_handler(self, rx_data):
        """ handler of ZDO_MGMT_NWK_DISC_REQ SRSP """
        if rx_data['id'] == ZpiCommand.ZDO_MGMT_NWK_DISC_REQ_SRSP:
            return struct.unpack('<B', rx_data['status'])[0]
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZDO_MGMT_NWK_DISC_REQ_SRSP, rx_data['id']))

    def zdo_mgmt_nwk_disc_rsp_handler(self, rx_data):
        if rx_data['id'] == ZpiCommand.ZDO_MGMT_NWK_DISC_RSP:
            src_addr = struct.unpack('<H', rx_data['src_addr'])[0]
            status = struct.unpack('<B', rx_data['status'])[0]
            nwk_cnt = struct.unpack('<B', rx_data['nwk_cnt'])[0]
            start_index = struct.unpack('<B', rx_data['start_index'])[0]
            nwk_list_cnt = struct.unpack('<B', rx_data['nwk_list_cnt'])[0]
            nwk_list_records = rx_data['nwk_list_records']

            nwk_records = []
            for record_index in range(0, nwk_list_cnt*6, 6):
                #contain each NWK Entry raw data, 6 bytes per entry
                nwk_records.append(nwk_list_records[record_index:(record_index + 6)])
            return (src_addr, status, nwk_cnt, start_index,
                    nwk_records)
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZDO_MGMT_NWK_DISC_RSP, rx_data['id']))

    def zdo_mgmt_lqi_req(self, dst_addr, start_index):
        """ request the destination device to return its neighbor table. """
        self._srsp_event_clear(ZpiCommand.ZDO_MGMT_LQI_REQ_SRSP)
        self.send(ZpiCommand.ZDO_MGMT_LQI_REQ,
                  dst_addr = struct.pack('<H', dst_addr),
                  start_index = struct.pack('<B', start_index))
        if self._srsp_event_wait(ZpiCommand.ZDO_MGMT_LQI_REQ_SRSP):
            return self._zdo_mgmt_lqi_req_srsp_handler(self._srsp_rx_msg)
        else:
            raise SrspTimeoutException()

    def _zdo_mgmt_lqi_req_srsp_handler(self, rx_data):
        """ handler of ZDO_MGMT_LQI_REQ SRSP """
        if rx_data['id'] == ZpiCommand.ZDO_MGMT_LQI_REQ_SRSP:
            return struct.unpack('<B', rx_data['status'])[0]
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZDO_MGMT_LQI_REQ_SRSP, rx_data['id']))

    def zdo_mgmt_lqi_rsp_handler(self, rx_data):
        if rx_data['id'] == ZpiCommand.ZDO_MGMT_LQI_RSP:
            src_addr = struct.unpack('<H', rx_data['src_addr'])[0]
            status = struct.unpack('<B', rx_data['status'])[0]
            nbr_table_entries = struct.unpack('<B', rx_data['nbr_table_entries'])[0]
            start_index = struct.unpack('<B', rx_data['start_index'])[0]
            nbr_table_list_cnt = struct.unpack('<B', rx_data['nbr_table_list_cnt'])[0]
            nbr_table_list_records = rx_data['nbr_table_list_records']

            nbr_table_records = []
            for record_index in range(0, nbr_table_list_cnt*22, 22):
                #contain each Nbr Table Entry raw data, 22 bytes per entry
                nbr_table_records.append(nbr_table_list_records[record_index:(record_index + 22)])
            return (src_addr, status, nbr_table_entries, start_index,
                    nbr_table_records)

        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZDO_MGMT_LQI_RSP, rx_data['id']))

    def zdo_mgmt_rtg_req(self, dst_addr, start_index):
        """ request the routing table of the destination device"""
        self._srsp_event_clear(ZpiCommand.ZDO_MGMT_RTG_REQ_SRSP)
        self.send(ZpiCommand.ZDO_MGMT_RTG_REQ,
                  dst_addr = struct.pack('<H', dst_addr),
                  start_index = struct.pack('<B', start_index))
        if self._srsp_event_wait(ZpiCommand.ZDO_MGMT_RTG_REQ_SRSP):
            return self._zdo_mgmt_rtg_req_srsp_handler(self._srsp_rx_msg)
        else:
            raise SrspTimeoutException()

    def _zdo_mgmt_rtg_req_srsp_handler(self, rx_data):
        """ handler of the ZDO_MGMT_RTG_REQ SRSP """
        if rx_data['id'] == ZpiCommand.ZDO_MGMT_RTG_REQ_SRSP:
            return struct.unpack('<B', rx_data['status'])[0]
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZDO_MGMT_RTG_REQ_SRSP, rx_data['id']))

    def zdo_mgmt_rtg_rsp_handler(self, rx_data):
        if rx_data['id'] == ZpiCommand.ZDO_MGMT_RTG_RSP:
            src_addr = struct.unpack('<H', rx_data['src_addr'])[0]
            status = struct.unpack('<B', rx_data['status'])[0]
            rtg_table_entries = struct.unpack('<B',
                                                  rx_data['rtg_table_entries'])[0]
            start_index = struct.unpack('<B', rx_data['start_index'])[0]
            rtg_table_list_cnt = struct.unpack('<B',
                                                   rx_data['rtg_table_list_cnt'])[0]
            rtg_table_list_records = rx_data['rtg_table_list_records']

            rtg_table_records = []
            for record_index in range(0, rtg_table_list_cnt*5, 5):
                #contain each rtg Table Entry raw data, 5 bytes per entry
                rtg_table_records.append(rtg_table_list_records[record_index:(record_index + 5)])
            return (src_addr, status, rtg_table_entries, start_index,
                    rtg_table_records)
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZDO_MGMT_RTG_RSP, rx_data['id']))

    def zdo_mgmt_bind_req(self, dst_addr, start_index):
        """ request the Binding Table of the destination device """
        self._srsp_event_clear(ZpiCommand.ZDO_MGMT_BIND_REQ_SRSP)
        self.send(ZpiCommand.ZDO_MGMT_BIND_REQ,
                  dst_addr = struct.pack('<H', dst_addr),
                  start_index = struct.pack('<B', start_index))
        if self._srsp_event_wait(ZpiCommand.ZDO_MGMT_BIND_REQ_SRSP):
            return self._zdo_mgmt_bind_req_srsp_handler(self._srsp_rx_msg)
        else:
            raise SrspTimeoutException()

    def _zdo_mgmt_bind_req_srsp_handler(self, rx_data):
        """ handler of the ZDO_MGMT_BIND_REQ SRSP """
        if rx_data['id'] == ZpiCommand.ZDO_MGMT_BIND_REQ_SRSP:
            return struct.unpack('<B', rx_data['status'])[0]
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZDO_MGMT_BIND_REQ_SRSP, rx_data['id']))

    def zdo_mgmt_bind_rsp_handler(self, rx_data):
        if rx_data['id'] == ZpiCommand.ZDO_MGMT_BIND_RSP:
            src_addr = struct.unpack('<H', rx_data['src_addr'])[0]
            status = struct.unpack('<B', rx_data['status'])[0]
            binding_table_entries = struct.unpack('<B',
                                                  rx_data['binding_table_entries'])[0]
            start_index = struct.unpack('<B', rx_data['start_index'])[0]
            binding_table_list_cnt = struct.unpack('<B',
                                                   rx_data['binding_table_list_cnt'])[0]
            binding_table_list_records = rx_data['binding_table_list_records']

            binding_table_records = []
            for record_index in range(0, binding_table_list_cnt*20, 20):
                #contain each Binding Table Entry raw data, 20byte per entry
                binding_table_records.append(binding_table_list_records[record_index:(record_index + 20)])
            return (src_addr, status, binding_table_entries, start_index,
                    binding_table_records)
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZDO_MGMT_BIND_RSP, rx_data['id']))

    def zdo_mgmt_leave_req(self, dst_addr, device_addr, remove_children_rejoin):
        """
            request a Management Leave Request for the target device and remove
            devices from the network
        """
        self._srsp_event_clear(ZpiCommand.ZDO_MGMT_LEAVE_REQ_SRSP)
        self.send(ZpiCommand.ZDO_MGMT_LEAVE_REQ,
                  dst_addr = struct.pack('<H', dst_addr),
                  device_addr = struct.pack('<Q', device_addr),
                  remove_children_rejoin = struct.pack('<B', remove_children_rejoin))
        if self._srsp_event_wait(ZpiCommand.ZDO_MGMT_LEAVE_REQ_SRSP):
            return self._zdo_mgmt_leave_req_srsp_handler(self._srsp_rx_msg)
        else:
            raise SrspTimeoutException()

    def _zdo_mgmt_leave_req_srsp_handler(self, rx_data):
        """ handler of the ZDO_MGMT_BIND_REQ SRSP """
        if rx_data['id'] == ZpiCommand.ZDO_MGMT_LEAVE_REQ_SRSP:
            return struct.unpack('<B', rx_data['status'])[0]
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZDO_MGMT_LEAVE_REQ_SRSP, rx_data['id']))

    def zdo_mgmt_leave_rsp_handler(self, rx_data):
        if rx_data['id'] == ZpiCommand.ZDO_MGMT_LEAVE_RSP:
            src_addr = struct.unpack('<H', rx_data['src_addr'])[0]
            status = struct.unpack('<B', rx_data['status'])[0]
            return src_addr, status
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZDO_MGMT_LEAVE_RSP, rx_data['id']))

    def zdo_mgmt_direct_join_req(self, dst_addr, device_addr, cap_info):
        """ request the Management Direct Join Request of a designated device"""
        self._srsp_event_clear(ZpiCommand.ZDO_MGMT_DIRECT_JOIN_REQ_SRSP)
        self.send(ZpiCommand.ZDO_MGMT_DIRECT_JOIN_REQ,
                  dst_addr = struct.pack('<H', dst_addr),
                  device_addr = struct.pack('<Q', device_addr),
                  cap_info = struct.pack('<B', cap_info))
        if self._srsp_event_wait(ZpiCommand.ZDO_MGMT_DIRECT_JOIN_REQ_SRSP):
            return self._zdo_mgmt_direct_join_req_srsp_handler(self._srsp_rx_msg)
        else:
            raise SrspTimeoutException()

    def _zdo_mgmt_direct_join_req_srsp_handler(self, rx_data):
        """ handler of the ZDO_MGMT_DIRECT_JOIN_REQ  SRSP """
        if rx_data['id'] == ZpiCommand.ZDO_MGMT_DIRECT_JOIN_REQ_SRSP:
            return struct.unpack('<B', rx_data['status'])[0]
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZDO_MGMT_DIRECT_JOIN_REQ_SRSP, rx_data['id']))


    def zdo_mgmt_direct_join_rsp_handler(self, rx_data):
        if rx_data['id'] == ZpiCommand.ZDO_MGMT_DIRECT_JOIN_RSP:
            src_addr = struct.unpack('<H', rx_data['src_addr'])[0]
            status = struct.unpack('<B', rx_data['status'])[0]
            return src_addr, status
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZDO_MGMT_DIRECT_JOIN_RSP, rx_data['id']))

    def zdo_mgmt_permit_join_req(self, dst_addr, duration, tc_significance):
        """ set the Permit Join for the destination device"""
        self._srsp_event_clear(ZpiCommand.ZDO_MGMT_PERMIT_JOIN_REQ_SRSP)
        self.send(ZpiCommand.ZDO_MGMT_PERMIT_JOIN_REQ,
                  addr_mode = struct.pack('<B', AddressMode.ADDRESS_16_BIT),   # 16-bit mode as default, moded for Z-Stack 2.6.1
                  dst_addr = struct.pack('<H', dst_addr),
                  duration = struct.pack('<B', duration),
                  tc_significance = struct.pack('<B', tc_significance))
        if self._srsp_event_wait(ZpiCommand.ZDO_MGMT_PERMIT_JOIN_REQ_SRSP):
            return self._zdo_mgmt_permit_join_req_srsp_handler(self._srsp_rx_msg)
        else:
            raise SrspTimeoutException()

    def _zdo_mgmt_permit_join_req_srsp_handler(self, rx_data):
        """ handler of the ZDO_MGMT_PERMIT_JOIN_REQ SRSP """
        if rx_data['id'] == ZpiCommand.ZDO_MGMT_PERMIT_JOIN_REQ_SRSP:
            return struct.unpack('<B', rx_data['status'])[0]
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZDO_MGMT_PERMIT_JOIN_REQ_SRSP, rx_data['id']))

    def zdo_mgmt_permit_join_rsp_handler(self, rx_data):
        if rx_data['id'] == ZpiCommand.ZDO_MGMT_PERMIT_JOIN_RSP:
            src_addr = struct.unpack('<H', rx_data['src_addr'])[0]
            status = struct.unpack('<B', rx_data['status'])[0]
            return src_addr, status
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZDO_MGMT_PERMIT_JOIN_RSP, rx_data['id']))


    #noinspection PyUnusedLocal
    def zdo_mgmt_nwk_update_req(self, dst_addr, dst_addr_mode, channel_mask,
                                scan_duration, scan_count, nwk_manager_addr):
        """
            allow updating of network configuration parameters or to request
            information from devices on network conditions in the local operating
            environment.
        """
        self._srsp_event_clear(ZpiCommand.ZDO_MGMT_NWK_UPDATE_REQ_SRSP)
        self.send(ZpiCommand.ZDO_MGMT_NWK_UPDATE_REQ,
                  dst_addr = struct.pack('<H', dst_addr),
                  dst_addr_mode = struct.pack('<B', dst_addr_mode),
                  channel_mask = struct.pack('<L', channel_mask),
                  scan_duration = struct.pack('<B', scan_duration),
                  nwk_manager_addr = struct.pack('<H', nwk_manager_addr))
        if self._srsp_event_set(ZpiCommand.ZDO_MGMT_NWK_UPDATE_REQ_SRSP):
            return self._zdo_mgmt_nwk_update_req_srsp_handler(self._srsp_rx_msg)
        else:
            raise SrspTimeoutException()

    def _zdo_mgmt_nwk_update_req_srsp_handler(self, rx_data):
        """ handler of the ZDO_MGMT_NWK_UPDATE_REQ SRSP """
        if rx_data['id'] == ZpiCommand.ZDO_MGMT_NWK_UPDATE_REQ_SRSP:
            return struct.unpack('<B', rx_data['status'])[0]
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZDO_MGMT_NWK_UPDATE_REQ_SRSP, rx_data['id']))

    def zdo_start_from_app(self, start_delay = 0):
        """ start the device in the network"""
        self._srsp_event_clear(ZpiCommand.ZDO_STARTUP_FROM_APP_SRSP)
        self.send(ZpiCommand.ZDO_STARTUP_FROM_APP,
                  start_delay = struct.pack('<H', start_delay))
        #it may take a bit long time for SRSP, typical 200ms ~ 400ms
        if self._srsp_event_wait(ZpiCommand.ZDO_STARTUP_FROM_APP_SRSP, 1.000):
            return self._zdo_start_from_app_srsp_handler(self._srsp_rx_msg)
        else:
            raise SrspTimeoutException()

    def _zdo_start_from_app_srsp_handler(self, rx_data):
        """ handler of ZDO_START_FROM_APP SRSP.
            note: the returned status value represents different meanings as
            general status.
                - 0x00: Restored network state
                - 0x01: New network state
                - 0x02: leave and not started
        """
        if rx_data['id'] == ZpiCommand.ZDO_STARTUP_FROM_APP_SRSP:
            return struct.unpack('<B', rx_data['status'])[0]
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZDO_STARTUP_FROM_APP_SRSP, rx_data['id']))

    def zdo_auto_find_destination(self, endpoint):
        """
            Issue a Match Descriptor Request for the requested endpoint.
            Note that this message has no repsonse. If there is a successful
            response to the Match Descriptor Request packet, the binding table
            on the device will be automatically updated.
        """
        self.send(ZpiCommand.ZDO_AUTO_FIND_DESTINATION,
                  endpoint = struct.pack('<B', endpoint))

    def zdo_set_link_key(self, short_addr, ieee_addr, link_key_data):
        """ set the application or trust center link key for a given device """
        self._srsp_event_clear(ZpiCommand.ZDO_SET_LINK_KEY_SRSP)
        self.send(ZpiCommand.ZDO_SET_LINK_KEY,
                  short_addr = struct.pack('<H', short_addr),
                  ieee_addr = struct.pack('<Q', ieee_addr),
                  link_key_data = link_key_data)
        if self._srsp_event_wait(ZpiCommand.ZDO_SET_LINK_KEY_SRSP):
            return self._zdo_set_link_key_srsp_handler(self._srsp_rx_msg)
        else:
            raise SrspTimeoutException()

    def _zdo_set_link_key_srsp_handler(self, rx_data):
        if rx_data['id'] == ZpiCommand.ZDO_SET_LINK_KEY_SRSP:
            return struct.unpack('<B', rx_data['status'])[0]
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZDO_SET_LINK_KEY_SRSP, rx_data['id']))

    def zdo_remove_link_key(self, ieee_addr):
        """ remove the application or trust center link key of a given deive """
        self._srsp_event_clear(ZpiCommand.ZDO_REMOVE_LINK_KEY_SRSP)
        self.send(ZpiCommand.ZDO_REMOVE_LINK_KEY,
                  ieee_addr = struct.pack('<Q', ieee_addr))
        if self._srsp_event_wait(ZpiCommand.ZDO_REMOVE_LINK_KEY_SRSP):
            return self._zdo_remove_link_key_srsp_handler(self._srsp_rx_msg)
        else:
            raise SrspTimeoutException()

    def _zdo_remove_link_key_srsp_handler(self, rx_data):
        if rx_data['id'] == ZpiCommand.ZDO_REMOVE_LINK_KEY_SRSP:
            return struct.unpack('<B', rx_data['status'])[0]
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZDO_REMOVE_LINK_KEY_SRSP, rx_data['id']))

    def zdo_get_link_key(self, ieee_addr):
        """ get the application or trust center link key of a given deive """
        self._srsp_event_clear(ZpiCommand.ZDO_GET_LINK_KEY_SRSP)
        self.send(ZpiCommand.ZDO_GET_LINK_KEY,
                  ieee_addr = struct.pack('<Q', ieee_addr))
        if self._srsp_event_wait(ZpiCommand.ZDO_GET_LINK_KEY_SRSP):
            return self._zdo_get_link_key_srsp_handler(self._srsp_rx_msg)
        else:
            raise SrspTimeoutException()

    def _zdo_get_link_key_srsp_handler(self, rx_data):
        if rx_data['id'] == ZpiCommand.ZDO_GET_LINK_KEY_SRSP:
            return struct.unpack('<B', rx_data['status'])[0]
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZDO_GET_LINK_KEY_SRSP, rx_data['id']))

    def zdo_nwk_discovery_req(self, scan_channels, scan_duration):
        """ initiate a Network Discovery (active scan) """
        self._srsp_event_clear(ZpiCommand.ZDO_NWK_DISCOVERY_REQ_SRSP)
        self.send(ZpiCommand.ZDO_NWK_DISCOVERY_REQ,
                  scan_channels = struct.pack('<L', scan_channels),
                  scan_duration = struct.pack('<B', scan_duration))
        if self._srsp_event_wait(ZpiCommand.ZDO_NWK_DISCOVERY_REQ_SRSP):
            return self._zdo_nwk_addr_req_srsp_handler(self._srsp_rx_msg)
        else:
            raise SrspTimeoutException()

    def _zdo_nwk_discovery_req_srsp_handler(self, rx_data):
        if rx_data['id'] == ZpiCommand.ZDO_NWK_DISCOVERY_REQ_SRSP:
            return struct.unpack('<B', rx_data['status'])[0]
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZDO_NWK_DISCOVERY_REQ_SRSP, rx_data['id']))

    def zdo_join_req(self, logical_channel, pan_id, pan_id_ext, chosen_parent,
                     parent_depth, stack_profile):
        """ request the device to join itself to a parent device on a network"""
        self._srsp_event_clear(ZpiCommand.ZDO_JOIN_REQ_SRSP)
        self.send(ZpiCommand.ZDO_JOIN_REQ,
                  logical_channel = struct.pack('<B', logical_channel),
                  pan_id = struct.pack('<H', pan_id),
                  pan_id_ext = struct.pack('<Q', pan_id_ext),
                  chosen_parent = struct.pack('<H', chosen_parent),
                  parent_depth = struct.pack('<B', parent_depth),
                  stack_profile = struct.pack('<B', stack_profile))
        if self._srsp_event_wait(ZpiCommand.ZDO_JOIN_REQ_SRSP):
            return self._zdo_join_req_srsp_handler(self._srsp_rx_msg)
        else:
            raise SrspTimeoutException()

    def _zdo_join_req_srsp_handler(self, rx_data):
        if rx_data['id'] == ZpiCommand.ZDO_JOIN_REQ_SRSP:
            return struct.unpack('<B', rx_data['status'])[0]
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZDO_JOIN_REQ_SRSP, rx_data['id']))

    def zdo_state_change_ind_handler(self, rx_data):
        if rx_data['id'] == ZpiCommand.ZDO_STATE_CHANGE_IND:
            state = struct.unpack('<B', rx_data['state'])[0]
            return state
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZDO_STATE_CHANGE_IND, rx_data['id']))

    def zdo_end_device_annce_ind_handler(self, rx_data):
        if rx_data['id'] == ZpiCommand.ZDO_END_DEVICE_ANNCE_IND:
            src_addr = struct.unpack('<H', rx_data['src_addr'])[0]
            nwk_addr = struct.unpack('<H', rx_data['nwk_addr'])[0]
            ieee_addr = struct.unpack('<Q', rx_data['ieee_addr'])[0]
            cap = struct.unpack('<B', rx_data['cap'])[0]
            return src_addr, nwk_addr, ieee_addr, cap
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZDO_END_DEVICE_ANNCE_IND, rx_data['id']))

    def zdo_status_error_rsp_handler(self, rx_data):
        if rx_data['id'] == ZpiCommand.ZDO_STATUS_ERROR_RSP:
            src_addr = struct.unpack('<H', rx_data['src_addr'])[0]
            status = struct.unpack('<B', rx_data['status'])[0]

            return src_addr, status
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZDO_STATUS_ERROR_RSP, rx_data['id']))

    def zdo_src_rtg_ind_handler(self, rx_data):
        if rx_data['id'] == ZpiCommand.ZDO_SRC_RTG_IND:
            dst_addr = struct.unpack('<H', rx_data['dst_addr'])[0]
            relay_cnt = struct.unpack('<B', rx_data['replay_cnt'])[0]
            relay_list = rx_data['relay_list']

            relays = []
            for index in range(0, relay_cnt*2, 2):
                relays.append(struct.unpack('<H',
                    relay_list[index:(index + 2)])[0])

            return dst_addr, relays
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZDO_SRC_RTG_IND, rx_data['id']))

    def zdo_leave_ind_handler(self, rx_data):
        """ handler of ZDO_LEAVE_IND AREQ """
        if rx_data['id'] == ZpiCommand.ZDO_LEAVE_IND:
            src_addr = struct.unpack('<H', rx_data['src_addr'])[0]
            ext_addr = struct.unpack('<Q', rx_data['ext_addr'])[0]
            request = struct.unpack('<B', rx_data['request'])[0]
            remove = struct.unpack('<B',  rx_data['remove'])[0]
            rejoin = struct.unpack('<B', rx_data['rejoin'])[0]

            return src_addr, ext_addr, request, remove, rejoin
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZDO_LEAVE_IND, rx_data['id']))

    def zdo_msg_cb_register(self, cluster_id):
        """
            register a ZDO callback and used in conjunction with the configuration
            item ZCD_NV_ZDO_DIRECT_CB.
        """
        self._srsp_event_clear(ZpiCommand.ZDO_MSG_CB_REGISTER_SRSP)
        self.send(ZpiCommand.ZDO_MSG_CB_REGISTER,
                  cluster_id = struct.pack('<H', cluster_id))
        if self._srsp_event_wait(ZpiCommand.ZDO_MSG_CB_REGISTER_SRSP):
            return self._zdo_msg_cb_register_srsp_handler(self._srsp_rx_msg)
        else:
            raise SrspTimeoutException()

    def _zdo_msg_cb_register_srsp_handler(self, rx_data):
        """ handler of ZDO_MSG_CB_REGISTER SRSP"""
        if rx_data['id'] == ZpiCommand.ZDO_MSG_CB_REGISTER_SRSP:
            return struct.unpack('<B', rx_data['status'])[0]
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZDO_MSG_CB_REGISTER_SRSP, rx_data['id']))

    def zdo_msg_cb_remove(self, cluster_id):
        """
            remove a ZDO callback and used in conjunction with the configuration
            item ZCD_NV_ZDO_DIRECT_CB.
        """
        self._srsp_event_clear(ZpiCommand.ZDO_MSG_CB_REMOVE_SRSP)
        self.send(ZpiCommand.ZDO_MSG_CB_REMOVE_REQ,
                  cluster_id = struct.pack('<H', cluster_id))
        if self._srsp_event_wait(ZpiCommand.ZDO_MSG_CB_REMOVE_SRSP):
            return self._zdo_msg_cb_remove_srsp_handler(self._srsp_rx_msg)
        else:
            raise SrspTimeoutException()

    def _zdo_msg_cb_remove_srsp_handler(self, rx_data):
        """ handler of ZDO_MSG_CB_REGISTER SRSP"""
        if rx_data['id'] == ZpiCommand.ZDO_MSG_CB_REMOVE_SRSP:
            return struct.unpack('<B', rx_data['status'])[0]
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZDO_MSG_CB_REMOVE_SRSP, rx_data['id']))

    def zdo_msg_cb_incoming_handler(self, rx_data):
        """ handler of ZDO_MSG_CB_INCOMING AREQ"""
        if rx_data['id'] == ZpiCommand.ZDO_MSG_CB_INCOMING:
            src_addr = struct.unpack('<H', rx_data['src_addr'])[0]
            was_broadcast = struct.unpack('<B', rx_data['was_broadcast'])[0]
            cluster_id = struct.unpack('<H', rx_data['cluster_id'])[0]
            security_use = struct.unpack('<B', rx_data['security_use'])[0]
            seq_num = struct.unpack('<B', rx_data['seq_num'])[0]
            mac_dst_addr = struct.unpack('<H', rx_data['mac_dst_addr'])[0]
            data = rx_data['data']
            return (src_addr, was_broadcast, cluster_id, security_use, seq_num,
                    mac_dst_addr, data)
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.ZDO_MSG_CB_INCOMING, rx_data['id']))

    #Util interface
    def util_data_req(self, security_use):
        """ send a one shot MAC MLME Poll Request (or data request) """
        self._srsp_event_clear(ZpiCommand.UTIL_DATA_REQ_SRSP)
        self.send(ZpiCommand.UTIL_DATA_REQ,
                  security_use=struct.pack('<B', security_use))
        if self._srsp_event_wait(ZpiCommand.UTIL_DATA_REQ_SRSP):
            return self._util_data_req_srsp_handler(self._srsp_rx_msg)
        else:
            raise SrspTimeoutException()

    def _util_data_req_srsp_handler(self, rx_data):
        """ handler of UTIL_DATA_REQ_SRSP"""
        if rx_data['id'] == ZpiCommand.UTIL_DATA_REQ_SRSP:
            status = struct.unpack('<B', rx_data['status'])[0]

            return status
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.UTIL_DATA_REQ_SRSP, rx_data['id']))

    def util_addrmgr_ext_addr_lookup(self, ext_addr):
        """ a proxy call to the AddrMgrEntryLookupExt() function """
        self._srsp_event_clear(ZpiCommand.UTIL_ADDRMGR_EXT_ADDR_LOOKUP_SRSP)
        self.send(ZpiCommand.UTIL_ADDRMGR_EXT_ADDR_LOOKUP,
                  struct.pack('<Q', ext_addr))
        if self._srsp_event_wait(ZpiCommand.UTIL_ADDRMGR_EXT_ADDR_LOOKUP_SRSP):
            return self._util_addrmgr_ext_addr_lookup_srsp_handler(self._srsp_rx_msg)
        else:
            raise SrspTimeoutException()

    def _util_addrmgr_ext_addr_lookup_srsp_handler(self, rx_data):
        """ handler of UTIL_ADDRMGR_EXT_ADDR_LOOKUP_SRSP """
        if rx_data['id'] == ZpiCommand.UTIL_ADDRMGR_EXT_ADDR_LOOKUP_SRSP:
            nwk_addr = struct.unpack('<B', rx_data['nwk_addr'])[0]

            return nwk_addr
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.UTIL_ADDRMGR_EXT_ADDR_LOOKUP_SRSP, rx_data['id']))

    def util_addrmgr_nwk_addr_lookup(self, nwk_addr):
        """ a proxy call to the AddrMgrEntryLookupNwk() function """
        self._srsp_event_clear(ZpiCommand.UTIL_ADDRMGR_NWK_ADDR_LOOKUP_SRSP)
        self.send(ZpiCommand.UTIL_ADDRMGR_NWK_ADDR_LOOKUP,
                  nwk_addr=struct.pack('<H', nwk_addr))
        if self._srsp_event_wait(ZpiCommand.UTIL_ADDRMGR_NWK_ADDR_LOOKUP_SRSP):
            return self._util_addrmgr_nwk_addr_lookup_srsp_handler(self._srsp_rx_msg)
        else:
            raise SrspTimeoutException()

    def _util_addrmgr_nwk_addr_lookup_srsp_handler(self, rx_data):
        """ handler of UTIL_ADDRMGR_NWK_ADDR_LOOKUP_SRSP """
        if rx_data['id'] == ZpiCommand.UTIL_ADDRMGR_NWK_ADDR_LOOKUP_SRSP:
            ext_addr = struct.unpack('<Q', rx_data['ext_addr'])[0]

            return ext_addr
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.UTIL_ADDRMGR_NWK_ADDR_LOOKUP_SRSP, rx_data['id']))

    def util_apsme_link_key_data_get(self, ext_addr):
        """ retrieves APS link security key, TX and RX frame counters"""
        self._srsp_event_clear(ZpiCommand.UTIL_APSME_LINK_KEY_DATA_GET_SRSP)
        self.send(ZpiCommand.UTIL_APSME_LINK_KEY_DATA_GET,
            ext_addr=struct.pack('<Q', ext_addr))
        if self._srsp_event_wait(ZpiCommand.UTIL_APSME_LINK_KEY_DATA_GET_SRSP):
            return self._util_apsme_link_key_data_get_srsp_handler(self._srsp_rx_msg)
        else:
            raise SrspTimeoutException()

    def _util_apsme_link_key_data_get_srsp_handler(self, rx_data):
        """ handler of UTIL_APSME_LINK_KEY_DATA_GET_SRSP """
        if rx_data['id'] == ZpiCommand.UTIL_APSME_LINK_KEY_DATA_GET_SRSP:
            status = struct.unpack('<B', rx_data['status'])[0]
            sec_key = rx_data['sec_key']  #just byte array raw data
            tx_frm_cntr = struct.unpack('<L', rx_data['tx_frm_cntr'])[0]
            rx_frm_cntr = struct.unpack('<L', rx_data['rx_frm_cntr'])[0]
            return status, sec_key, tx_frm_cntr, rx_frm_cntr
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.UTIL_APSME_LINK_KEY_DATA_GET_SRSP, rx_data['id']))

    def util_apsme_link_key_nv_id_get(self, ext_addr):
        """
            a proxy call to the APSME_LinkKeyNvIdGet() function. It returns the
            NV ID code corresponding to a device with the specified extended
            address
        """
        self._srsp_event_clear(ZpiCommand.UTIL_APSME_LINK_KEY_NV_ID_GET_SRSP)
        self.send(ZpiCommand.UTIL_APSME_LINK_KEY_NV_ID_GET,
                  ext_addr = struct.pack('<Q', ext_addr))
        if self._srsp_event_wait(ZpiCommand.UTIL_APSME_LINK_KEY_NV_ID_GET_SRSP):
            return self._util_apsme_link_key_nv_id_get_srsp_handler(self._srsp_rx_msg)
        else:
            raise SrspTimeoutException()

    def _util_apsme_link_key_nv_id_get_srsp_handler(self, rx_data):
        """ handler of UTIL_APSME_LINK_KEY_MV_ID_GET_SRSP """
        if rx_data['id'] == ZpiCommand.UTIL_APSME_LINK_KEY_NV_ID_GET_SRSP:
            status = struct.unpack('<B', rx_data['status'])[0]
            link_key_nv_id = struct.unpack('<H', rx_data['link_key_nv_id'])[0]
            return status, link_key_nv_id
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.UTIL_APSME_LINK_KEY_NV_ID_GET_SRSP, rx_data['id']))

    def util_apsme_request_key_cmd(self, partner_addr):
        """
            send a request key to the trust center from an originator device
            who wants to exchange messages with a partner device
        """
        self._srsp_event_clear(ZpiCommand.UTIL_APSME_REQUEST_KEY_CMD_SRSP)
        self.send(ZpiCommand.UTIL_APSME_REQUEST_KEY_CMD,
            partner_addr=struct.pack('<Q', partner_addr))
        if self._srsp_event_wait(ZpiCommand.UTIL_APSME_REQUEST_KEY_CMD_SRSP):
            return self._util_apsme_request_key_cmd_srsp_handler(self._srsp_rx_msg)
        else:
            raise SrspTimeoutException()

    def _util_apsme_request_key_cmd_srsp_handler(self, rx_data):
        """ handler of UTIL_APSME_REQUEST_KEY_CMD_SRSP"""
        if rx_data['id'] == ZpiCommand.UTIL_APSME_REQUEST_KEY_CMD_SRSP:
            status = struct.unpack('<B', rx_data['status'])[0]
            return status
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.UTIL_APSME_REQUEST_KEY_CMD_SRSP, rx_data['id']))

    def util_assoc_count(self, start_relation, end_relation):
        """ request for associated device count
            according Z-Stack nwk_globals.h definition:
                #define NWK_MAX_DEVICE_LIST     20  // Maximum number of devices
                                                    //in the Assoc/Device list.
        """
        self._srsp_event_clear(ZpiCommand.UTIL_ASSOC_COUNT_SRSP)
        self.send(ZpiCommand.UTIL_ASSOC_COUNT,
                  start_relation = struct.pack('<B', start_relation),
                  end_relation = struct.pack('<B', end_relation))
        if self._srsp_event_wait(ZpiCommand.UTIL_ASSOC_COUNT_SRSP):
            return self._util_assoc_count_srsp_handler(self._srsp_rx_msg)
        else:
            raise SrspTimeoutException

    def _util_assoc_count_srsp_handler(self, rx_data):
        """ handler for UTIL_ASSOC_COUNT srsp"""
        if rx_data['id'] == ZpiCommand.UTIL_ASSOC_COUNT_SRSP:
            count = struct.unpack('<H', rx_data['count'])[0]
            return count
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.UTIL_ASSOC_COUNT_SRSP, rx_data['id']))

    def util_assoc_find_device(self, number):
        """ find the N-th assoc device """
        self._srsp_event_clear(ZpiCommand.UTIL_ASSOC_FIND_DEVICE_SRSP)
        self.send(ZpiCommand.UTIL_ASSOC_FIND_DEVICE,
                  number = struct.pack('<B', number))
        if self._srsp_event_wait(ZpiCommand.UTIL_ASSOC_FIND_DEVICE_SRSP):
            return self._util_assoc_find_device_srsp_handler(self._srsp_rx_msg)
        else:
            raise SrspTimeoutException

    def _util_assoc_find_device_srsp_handler(self, rx_data):
        """ handler for UTIL_ASSOC_FIND_DEVICE srsp"""
        if rx_data['id'] == ZpiCommand.UTIL_ASSOC_FIND_DEVICE_SRSP:
            device_unpacked = struct.unpack('<HHBBBBBBBBLH', rx_data['device'])
            device = {}
            attr_index = 0
            for attr_name in AssociatedDevice.attr_names:
                device[attr_name] = device_unpacked[attr_index]
                attr_index += 1

            return device
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.UTIL_ASSOC_FIND_DEVICE_SRSP, rx_data['id']))

    def util_zcl_key_est_init_est(self, task_id, seq_num, endpoint, addr_mode,
                                  addr):
        pass

    def util_zcl_key_est_sign(self, input_data):
        pass

    def util_zcl_key_establish_ind_handler(self, rx_data):
        pass

    def util_test_loopback(self, test_data):
        pass


    def aps_add_group(self, endpoint, group_id, group_name = b''):
        """ add a group in APS group table """
        self._srsp_event_clear(ZpiCommand.APS_ADD_GROUP_SRSP)

        #group_name length check
        if group_name is None:
            group_name = b''

        if len(group_name) < 16:
            #add white space
            group_name += (16 - len(group_name)) * b' '
        else :
            group_name = group_name[:16]   #only the leading 16chars left

        self.send(ZpiCommand.APS_ADD_GROUP,
                  endpoint = struct.pack('<B', endpoint),
                  group_id = struct.pack('<H', group_id),
                  group_name = group_name)

        #test result: add group needs ~230ms,
        if self._srsp_event_wait(ZpiCommand.APS_ADD_GROUP_SRSP, 0.500):
            return self._aps_add_group_srsp_handler(self._srsp_rx_msg)
        else:
            raise SrspTimeoutException()

    def _aps_add_group_srsp_handler(self, rx_data):
        """ handler of APS_ADD_GROUP_SRSP """
        if rx_data['id'] == ZpiCommand.APS_ADD_GROUP_SRSP:
            status = struct.unpack('<B', rx_data['status'])[0]

            return status
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.APS_ADD_GROUP_SRSP, rx_data['id']))

    def aps_remove_group(self, endpoint, group_id):
        """ remove a group from the aps group table """
        self._srsp_event_clear(ZpiCommand.APS_REMOVE_GROUP_SRSP)
        self.send(ZpiCommand.APS_REMOVE_ALL_GROUP,
                  endpoint = struct.pack('<B', endpoint),
                  group_id = struct.pack('<H', group_id))
        if self._srsp_event_wait(ZpiCommand.APS_REMOVE_GROUP_SRSP, 0.500):
            return self._aps_remove_group_srsp_handler(self._srsp_rx_msg)
        else:
            raise SrspTimeoutException()

    def _aps_remove_group_srsp_handler(self, rx_data):
        """ handler of APS_REMOVE_GROUP_SRSP """
        if rx_data['id'] == ZpiCommand.APS_REMOVE_GROUP_SRSP:
            status = struct.unpack('<B', rx_data['status'])[0]

            return status
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.APS_REMOVE_GROUP_SRSP, rx_data['id']))

    def aps_remove_all_group(self, endpoint):
        """ remove all groups from aps group table for a specified endpoint """
        self._srsp_event_clear(ZpiCommand.APS_REMOVE_ALL_GROUP_SRSP)
        self.send(ZpiCommand.APS_REMOVE_ALL_GROUP,
                  endpoint = struct.pack('<B', endpoint))
        if self._srsp_event_wait(ZpiCommand.APS_REMOVE_ALL_GROUP_SRSP, 0.500):
            return self._aps_remove_all_groups_srsp_handler(self._srsp_rx_msg)
        else:
            raise SrspTimeoutException()

    def _aps_remove_all_groups_srsp_handler(self, rx_data):
        """ handler of APS_COUNT_ALL_GROUPS_SRSP """
        if rx_data['id'] == ZpiCommand.APS_REMOVE_ALL_GROUP_SRSP:
            status = struct.unpack('<B', rx_data['status'])[0]

            return status
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.APS_REMOVE_ALL_GROUP_SRSP, rx_data['id']))

    def aps_find_group(self, endpoint, group_id):
        """ find a group in aps group table """
        self._srsp_event_clear(ZpiCommand.APS_FIND_GROUP_SRSP)
        self.send(ZpiCommand.APS_FIND_GROUP,
                  endpoint = struct.pack('<B', endpoint),
                  group_id = struct.pack('<H', group_id))
        if self._srsp_event_wait(ZpiCommand.APS_FIND_GROUP_SRSP, 0.500):
            return self._aps_find_group_srsp_handler(self._srsp_rx_msg)
        else:
            raise SrspTimeoutException()

    def _aps_find_group_srsp_handler(self, rx_data):
        """ handler of APS_FIND_GROUP_SRSP """
        if rx_data['id'] == ZpiCommand.APS_FIND_GROUP_SRSP:
            status = struct.unpack('<B', rx_data['status'])[0]
            endpoint = struct.unpack('<B', rx_data['endpoint'])[0]
            group_id = struct.unpack('<H', rx_data['group_id'])[0]
            group_name = rx_data['group_name']

            return status, endpoint, group_id, group_name
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.APS_FIND_GROUP_SRSP, rx_data['id']))

    def aps_find_all_groups_for_endpoint(self, endpoint):
        """ find all groups for a specified endpoint in aps group table """
        self._srsp_event_clear(ZpiCommand.APS_FIND_ALL_GROUPS_FOR_EP_SRSP)
        self.send(ZpiCommand.APS_FIND_ALL_GROUPS_FOR_EP,
                  endpoint = struct.pack('<B', endpoint))
        if self._srsp_event_wait(ZpiCommand.APS_FIND_ALL_GROUPS_FOR_EP_SRSP):
            return self._aps_find_all_groups_for_endpoint_srsp_handler(self._srsp_rx_msg)
        else:
            raise SrspTimeoutException()

    def _aps_find_all_groups_for_endpoint_srsp_handler(self, rx_data):
        """ handler of APS_COUNT_ALL_GROUPS_SRSP """
        if rx_data['id'] == ZpiCommand.APS_FIND_ALL_GROUPS_FOR_EP_SRSP:
            status = struct.unpack('<B', rx_data['status'])[0]
            endpoint = struct.unpack('<B', rx_data['endpoint'])[0]
            group_cnt = struct.unpack('<B', rx_data['group_cnt'])[0]

            group_ids = []
            if group_cnt > 0:
                group_id_list = rx_data['group_id_list']
                for index in range(0, group_cnt*2, 2):
                    group_ids.append(struct.unpack('<H', group_id_list[index:(index+2)])[0])

            return status, endpoint, group_ids
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.APS_FIND_ALL_GROUPS_FOR_EP_SRSP, rx_data['id']))


    def aps_count_all_groups(self):
        """ """
        self._srsp_event_clear(ZpiCommand.APS_COUNT_ALL_GROUPS_SRSP)
        self.send(ZpiCommand.APS_COUNT_ALL_GROUPS)
        if self._srsp_event_wait(ZpiCommand.APS_COUNT_ALL_GROUPS_SRSP):
            return self._aps_count_all_groups_srsp_handler(self._srsp_rx_msg)  #FIXME
        else:
            raise SrspTimeoutException()

    def _aps_count_all_groups_srsp_handler(self, rx_data):
        """ handler of APS_COUNT_ALL_GROUPS_SRSP """
        if rx_data['id'] == ZpiCommand.APS_COUNT_ALL_GROUPS_SRSP:
            status = struct.unpack('<B', rx_data['status'])[0]
            group_cnt = struct.unpack('<B', rx_data['group_cnt'])[0]

            return status, group_cnt
        else:
            raise ValueError('Invalid Rx frame! Expected: %s, Received: %s' % (
                    ZpiCommand.APS_COUNT_ALL_GROUPS_SRSP, rx_data['id']))



class SerialTimeoutException(Exception):
    """ just a user-defined exception class for serial read/write time out"""
    pass

class SrspTimeoutException(Exception):
    """ just a user-defined exception class for Srsp response time out"""
    pass

class AreqTimeoutException(Exception):
    """ just a user-defined exception class for Areq response time out"""
    pass

class ResetType(object):
    HARD_RESET = 0x00
    SOFT_RESET = 0x01

class ResetReason(object):
    POWERUP = 0x00
    EXTERNAL = 0x01
    WATCHDOG = 0x02

    names = {
        POWERUP : 'POWERUP',
        EXTERNAL : 'EXTERNAL',
        WATCHDOG : 'WATCHDOG',
        }

    @classmethod
    def get_name(cls, reason):
        if reason in cls.names:
            return cls.names[reason]
        else:
            return 'Unknown reason'


class AdcResolution(object):
    _7_BIT = 0x00
    _9_BIT = 0x01
    _10_BIT = 0x02
    _12_BIT = 0x03

class GpioOperation(object):
    SET_DIRECTION = 0x00
    SET_INPUT_MODE = 0x01
    SET = 0x02
    CLEAR = 0x03
    TOGGLE = 0x04
    READ = 0x05

class ConfigParameter(object):
    """ ZNP device specific configuration parameters enumerations"""

    class Device(object):
        ZCD_NV_EXTADDR = 0x0001         #only listed in Z-Tool->Configuration dialog
        ZCD_NV_STARTUP_OPTION = 0x0003
        ZCD_NV_LOGICAL_TYPE = 0x0087
        ZCD_NV_ZDO_DIRECT_CB = 0x008f
        ZCD_NV_POLL_RATE = 0x0024
        ZCD_NV_QUEUED_POLL_RATE = 0x0025
        ZCD_NV_RESPONSE_POLL_RATE = 0x0026
        ZCD_NV_POLL_FAILURE_RETRIES = 0x0029
        ZCD_NV_INDIRECT_MSG_TIMEOUT = 0x002b
        ZCD_NV_APS_FRAME_RETRIES = 0x0043
        ZCD_NV_APS_ACK_WAIT_DURATION = 0x0044
        ZCD_NV_BINDING_TIME = 0x0046
        ZCD_NV_APSF_WINDOW_SIZE = 0x0049
        ZCD_NV_APSF_INTERFRAME_DELAY = 0x004a
        ZCD_NV_USERDESC = 0x0081

    class Network(object):
        """ ZNP network specific configuration parameters enumerations"""
        ZCD_NV_PANID = 0x0083
        ZCD_NV_CHANLIST = 0x0084
        ZCD_NV_PRECFGKEY = 0x0062
        ZCD_NV_PRECFGKEYS_ENABLE = 0x0063
        ZCD_NV_SECURITY_MODE = 0x0064
        ZCD_NV_USE_DEFAULT_TCLK = 0x006d
        ZCD_NV_BCAST_RETRIES = 0x002e
        ZCD_NV_PASSIVE_ACK_TIMEOUT = 0x002f
        ZCD_NV_BCAST_DELIVERY_TIME = 0x0030
        ZCD_NV_ROUTE_EXPIRY_TIME = 0x002c
        ZNP_NV_RF_TEST_PARAMS = 0x0f07

    uint8_type = (
        Device.ZCD_NV_STARTUP_OPTION,
        Device.ZCD_NV_LOGICAL_TYPE,
        Device.ZCD_NV_ZDO_DIRECT_CB ,
        Device.ZCD_NV_POLL_FAILURE_RETRIES,
        Device.ZCD_NV_INDIRECT_MSG_TIMEOUT,
        Device.ZCD_NV_APS_FRAME_RETRIES,
        Network.ZCD_NV_SECURITY_MODE,
        Network.ZCD_NV_PRECFGKEYS_ENABLE,
        Network.ZCD_NV_USE_DEFAULT_TCLK,
        Network.ZCD_NV_BCAST_RETRIES,
        Network.ZCD_NV_PASSIVE_ACK_TIMEOUT,
        Network.ZCD_NV_BCAST_DELIVERY_TIME,
        Network.ZCD_NV_ROUTE_EXPIRY_TIME)

    uint16_type = (
        Device.ZCD_NV_POLL_RATE,
        Device.ZCD_NV_QUEUED_POLL_RATE,
        Device.ZCD_NV_RESPONSE_POLL_RATE,
        Device.ZCD_NV_APS_ACK_WAIT_DURATION,
        Device.ZCD_NV_BINDING_TIME,
        Network.ZCD_NV_PANID)

    uint32_type = (
        Network.ZCD_NV_CHANLIST,
        )
    uint64_type = (
        Device.ZCD_NV_EXTADDR,
        )
    array_4bytes_type = (
        Network.ZNP_NV_RF_TEST_PARAMS,
        )
    array_16bytes_type = (
        Network.ZCD_NV_PRECFGKEY,
        )
    user_defined_type = (
        Device.ZCD_NV_USERDESC,
        )

class StartupOption(object):
    """ startup options """
    NONE_MASK = 0x00
    CLEAR_STATE_MASK = 0b00000010
    CLEAR_CONFIG_MASK = 0b00000000

class LogicalType(object):
    """ device logical type """
    COORDINATOR = 0x00
    ROUTER = 0x01
    ENDDEVICE = 0x02

    logical_types = (COORDINATOR, ROUTER, ENDDEVICE)
    logical_type_str = ('Coordinator', 'Router', 'End Device')

    @classmethod
    def get_description(cls, logical_type):
        if logical_type in cls.logical_types:
            return cls.logical_type_str[logical_type]
        else:
            return 'Unknown logical type'

class DeviceState(object):
    """ ZDO state enumerations """
    DEV_HOLD = 0
    DEV_INIT = 1
    DEV_NWK_DISC = 2
    DEV_NWK_JOINING = 3
    DEV_NWK_REJOIN = 4
    DEV_END_DEVICE_UNAUTH = 5
    DEV_END_DEVICE = 6
    DEV_ROUTER = 7
    DEV_COORD_STARTING = 8
    DEV_ZB_COORD = 9
    DEV_NWK_ORPHAN = 10

    state_str = (
        'Initialized-not started automatically',
        'Initialized-not connected to anything',
        'Discovery PANs to join',
        'Joining a PAN',
        'Rejoining a PAN, only for end devices',
        'Joined but not authenticated by trust center',
        'Started as end device after authentication',
        'Device joined, authenticated and is a router',
        'Starting as ZigBee coordinator',
        'Started as ZigBee coordinator',
        'Device has lost its information about its parent'
        )

    state_name = (
        'DEV_HOLD',
        'DEV_INIT',
        'DEV_NWK_DISC',
        'DEV_NWK_JOINING',
        'DEV_NWK_REJOIN',
        'DEV_END_DEVICE_UNAUTH',
        'DEV_END_DEVICE',
        'DEV_ROUTER',
        'DEV_COORD_STARTING',
        'DEV_ZB_COORD',
        'DEV_NWK_ORPHAN'
        )

    @classmethod
    def get_description(cls, state):
        return cls.state_str[state]

    @classmethod
    def get_name(cls, state):
        return cls.state_name[state]

class TxOptions(object):
    """ AF Tx Options enumerations """
    AF_ACK_REQUEST = 0x10
    AF_DISC_ROUTE = 0x20
    AF_EN_SECURITY = 0x40

class AddressShort(object):
    """ some short address constants """
    GROUP_ROUTE_COORD = 0xfffc
    GROUP_ALL_RECEIVER_ON = 0xfffd
    GROUP_BINDING = 0xfffe
    BROADCAST = 0xffff

class AddressMode(object):
    """ address mode enumerations """
    ADDRESS_NOT_PRESENT = 0x00
    GROUP_ADDRESS = 0x01
    ADDRESS_16_BIT = 0x02
    ADDRESS_64_BIT = 0x03
    BROADCAST = 0x0f

    address_modes = [
        ADDRESS_NOT_PRESENT,
        GROUP_ADDRESS,
        ADDRESS_16_BIT,
        ADDRESS_64_BIT,
        BROADCAST]

class DeviceInfoParameter(object):
    """ device info parameter for req/rsp: ZB_GET_DEVICE_INFO """
    STATE = 0
    IEEE_ADDR = 1
    NWK_ADDR = 2
    PARENT_NWK_ADDR = 3
    PARENT_IEEE_ADDR = 4
    CHANNEL = 5
    PAN_ID = 6
    EXT_PAN_ID = 7

    params_len = {
        STATE: 1,
        IEEE_ADDR: 8,
        NWK_ADDR: 2,
        PARENT_NWK_ADDR: 2,
        PARENT_IEEE_ADDR: 8,
        CHANNEL: 1,
        PAN_ID: 2,
        EXT_PAN_ID: 8
        }

class NodeRelation(object):
    """ node relation when used in associate count request """
    PARENT = 0
    CHILD_RFD = 1
    CHILD_RFD_RX_IDLE = 2
    CHILD_FFD = 3
    CHILD_FFD_RX_IDLE = 4
    NEIGHBOR = 5
    OTHER = 6

    RELATION_MAX = OTHER

    relation_names = (
        'PARENT',
        'CHILD_RFD',
        'CHILD_RFD_RX_IDLE',
        'CHILD_FFD',
        'CHILD_FFD_RX_IDLE',
        'NEIGHBOR',
        'OTHER'
        )
    relation_descriptions = (
        'Parent',
        'Child RFD',
        'Child RFD Rx Idle',
        'Child FFD',
        'Child FFD Rx Idle',
        'Neighbor',
        'Other'
        )

    @classmethod
    def get_name(cls, relation):
        return cls.relation_names[relation]

    @classmethod
    def get_description(cls, relation):
        return cls.relation_descriptions[relation]

class AssociatedDevice(object):
    attr_names = (
        'addr_short',
        'addr_index',
        'node_relation',
        'dev_status',
        'assoc_cnt',
        'age',
        'tx_counter',
        'tx_cost',
        'rx_lqi',
        'in_key_seq_num',
        'in_frm_cntr',
        'tx_failure'
        )

class BindAction(object):
    """ actions used in ZB_BIND_DEVICE command """
    DELETE_BIND = 0
    CREATE_BIND = 1

class InterPanCtlCommand(object):
    """ command enumertion for AF_INTER_PAN_CTL """
    INTER_PAN_CLR = 0x00
    INTER_PAN_SET = 0x01
    INTER_PAN_REG = 0x02
    INTER_PAN_CHK = 0x03

    @classmethod
    def get_data_len(cls, cmd):
        if cmd == cls.INTER_PAN_CLR:
            return 0
        elif cmd == cls.INTER_PAN_SET or cmd == cls.INTER_PAN_REG:
            return 1
        elif cmd == cls.INTER_PAN_CHK:
            return 4
        else:
            raise ValueError('Invalid inter-pan control command!')

    @classmethod
    def data_pack(cls, cmd, value):
        if cmd == cls.INTER_PAN_CLR:
            return b''
        elif cmd == cls.INTER_PAN_SET or cmd == cls.INTER_PAN_REG:
            return struct.pack('<B', value)
        elif cmd == cls.INTER_PAN_CHK:
            return struct.pack('<L', value)
        else:
            raise ValueError('Invalid inter-pan control command!')

    @classmethod
    def data_unpack(cls, cmd, data):
        if cmd == cls.INTER_PAN_CLR:
            return None
        elif cmd == cls.INTER_PAN_SET or cmd == cls.INTER_PAN_REG:
            return struct.unpack('<B', data)[0]
        elif cmd == cls.INTER_PAN_CHK:
            return struct.unpack('<L', data)[0]
        else:
            raise ValueError('Invalid inter-pan control command!')

class LatencyReq(object):
    """ latency requirement, for ZigBee the only applicable value is 0x00 """
    NO_LATENCY = 0x00
    FAST_BEACONS = 0x01
    SLOW_BEACONSS = 0x02
    ZB_DEFAULT = NO_LATENCY


class ZpiStatus(object):
    """ CC2530-ZNP return status enumerations """
    Z_SUCCESS = 0X00
    Z_FAILURE = 0x01    #Not defined in ZNP spec, found in ZPI doc and src code
    Z_INVALID_PARAMETER = 0X02
    ZMEM_ERROR = 0X10
    ZBUFFER_FULL = 0X11
    ZUNSUPPORTED_MODE = 0X12
    ZMAC_MEM_ERROR = 0X13
    ZB_INIT = 0x22
    ZDO_INVALID_REQUEST_TYPE = 0X80
    ZDO_INVALID_ENDPOINT = 0X82
    ZDO_UNSUPPORTED = 0X84
    ZDO_TIMEOUT = 0X85
    ZDO_NO_MATCH = 0X86
    ZDO_TABLE_FULL = 0X87
    ZDO_NO_BIND_ENTRY = 0X88
    ZSEC_NO_KEY = 0XA1
    ZSEC_MAX_FRM_COUNT = 0XA3
    ZAPS_FAIL = 0XB1
    ZAPS_TABLE_FULL = 0XB2
    ZAPS_ILLEGAL_REQUEST = 0XB3
    ZAPS_INVALID_BINDING = 0XB4
    ZAPS_UNSUPPORTED_ATTRIB = 0XB5
    ZAPS_NOT_SUPPORTED = 0XB6
    ZAPS_NO_ACK = 0XB7
    ZAPS_DUPLICATE_ENTRY = 0XB8
    ZAPS_NOBOUND_DEVICE = 0XB9
    ZNWK_INVALID_PARAM = 0XC1
    ZNWK_INVALID_REQUEST = 0XC2
    ZNWK_NOT_PERMITTED = 0XC3
    ZNWK_STARTUP_FAILURE = 0XC4
    ZNWK_TABLE_FULL = 0XC7
    ZNWK_UNKNOWN_DEVICE = 0XC8
    ZNWK_UNSUPPORTED_ATTRIBUTE = 0XC9
    ZNWK_NO_NETWORKS = 0XCA
    ZNWK_LEAVE_UNCONFIRMED = 0XCB
    ZNWK_NO_ACK = 0XCC
    ZNWK_NO_ROUTE = 0XCD
    ZMAC_NO_ACK = 0XE9

    status_names = {
        Z_SUCCESS: 'Success',
        Z_FAILURE: 'Failure',    #Not defined in ZNP spec, found in ZPI doc and src code
        Z_INVALID_PARAMETER: 'Z_INVALID_PARAMETER',
        ZMEM_ERROR: 'ZMEM_ERROR',
        ZBUFFER_FULL: 'ZBUFFER_FULL',
        ZUNSUPPORTED_MODE: 'ZUNSUPPORTED_MODE',
        ZMAC_MEM_ERROR: 'ZMAC_MEM_ERROR',
        ZB_INIT: 'ZB_INIT',      #not defined in ZNP return values but described in $4.3.3.2
        ZDO_INVALID_REQUEST_TYPE: 'ZDO_INVALID_REQUEST_TYPE',
        ZDO_INVALID_ENDPOINT: 'ZDO_INVALID_ENDPOINT',
        ZDO_UNSUPPORTED: 'ZDO_UNSUPPORTED',
        ZDO_TIMEOUT: 'ZDO_TIMEOUT',
        ZDO_NO_MATCH: 'ZDO_NO_MATCH',
        ZDO_TABLE_FULL: 'ZDO_TABLE_FULL',
        ZDO_NO_BIND_ENTRY: 'ZDO_NO_BIND_ENTRY',
        ZSEC_NO_KEY: 'ZSEC_NO_KEY',
        ZSEC_MAX_FRM_COUNT: 'ZSEC_MAX_FRM_COUNT',
        ZAPS_FAIL: 'ZAPS_FAIL',
        ZAPS_TABLE_FULL: 'ZAPS_TABLE_FULL',
        ZAPS_ILLEGAL_REQUEST: 'ZAPS_ILLEGAL_REQUEST',
        ZAPS_INVALID_BINDING: 'ZAPS_INVALID_BINDING',
        ZAPS_UNSUPPORTED_ATTRIB: 'ZAPS_UNSUPPORTED_ATTRIB',
        ZAPS_NOT_SUPPORTED: 'ZAPS_NOT_SUPPORTED',
        ZAPS_NO_ACK: 'ZAPS_NO_ACK',
        ZAPS_DUPLICATE_ENTRY: 'ZAPS_DUPLICATE_ENTRY',
        ZAPS_NOBOUND_DEVICE: 'ZAPS_NOBOUND_DEVICE',
        ZNWK_INVALID_PARAM: 'ZNWK_INVALID_PARAM',
        ZNWK_INVALID_REQUEST: 'ZNWK_INVALID_REQUEST',
        ZNWK_NOT_PERMITTED: 'ZNWK_NOT_PERMITTED',
        ZNWK_STARTUP_FAILURE: 'ZNWK_STARTUP_FAILURE',
        ZNWK_TABLE_FULL: 'ZNWK_TABLE_FULL',
        ZNWK_UNKNOWN_DEVICE: 'ZNWK_UNKNOWN_DEVICE',
        ZNWK_UNSUPPORTED_ATTRIBUTE: 'ZNWK_UNSUPPORTED_ATTRIBUTE',
        ZNWK_NO_NETWORKS: 'ZNWK_NO_NETWORKS',
        ZNWK_LEAVE_UNCONFIRMED: 'ZNWK_LEAVE_UNCONFIRMED',
        ZNWK_NO_ACK: 'ZNWK_NO_ACK',
        ZNWK_NO_ROUTE: 'ZNWK_NO_ROUTE',
        ZMAC_NO_ACK: 'ZMAC_NO_ACK',
        }
    @classmethod
    def get_name(cls, status):
        if status in cls.status_names:
            return cls.status_names[status]
        else:
            return 'Unknown status'

class ZdoStartupFromAppStatus(object):
    """this status class only for ZDO_STARTUP_FROM_APP SRSP, because it has a
    different meaning from general ZpiStatus """
    RESTORED_NETWORK_STATE = 0x00
    NEW_NETWORK_STATE = 0x01
    LEAVE_AND_NOT_STARTED = 0x02

    __status_names = {
        RESTORED_NETWORK_STATE: 'RESTORED_NETWORK_STATE',
        NEW_NETWORK_STATE: 'NEW_NETWORK_STATE',
        LEAVE_AND_NOT_STARTED: 'LEAVE_AND_NOT_STARTED',
    }

    @classmethod
    def get_name(cls, status):
        if status in cls.__status_names:
            return cls.__status_names[status]
        else:
            return 'Unknown status'


class ZdoNodeDescriptorResponse(object):
    """ ZDO node descriptor response class"""
    def __init__(self, src_addr, status, nwk_addr, logical_type_flags,
                 aps_flags,  mac_cap_flags, mnfr_code, max_buf_size,
                 max_trans_size, server_mask, max_out_trans_size,
                 descriptor_cap):
        self.src_addr = src_addr
        self.status = status
        self.nwk_addr = nwk_addr
        self.logical_type_flags = logical_type_flags
        self.aps_flags = aps_flags
        self.mac_cap_flags = mac_cap_flags
        self.mnfr_code = mnfr_code
        self.max_buf_size = max_buf_size
        self.max_trans_size = max_trans_size
        self.server_mask = server_mask
        self.max_out_trans_size = max_out_trans_size
        self.descriptor_cap = descriptor_cap

class ZdoPowerDescriptorResponse(object):
    """ ZDO power descriptor response class """
    def __init__(self, src_addr, status, nwk_addr, cur_pwrmode_avail_pwrsrc,
                 cur_pwrsrc_and_level):
        self.src_addr = src_addr
        self.status = status
        self.nwk_addr = nwk_addr
        self.cur_pwrmode_avail_pwrsrc = cur_pwrmode_avail_pwrsrc
        self.cur_pwrsrc_and_level = cur_pwrsrc_and_level

class ZdoSimpleDescriptorResponse(object):
    """ZDO simple descriptor response """
    def __init__(self, src_addr, status, nwk_addr, length, endpoint, profile_id,
                 device_id, device_ver, in_clusters, out_clusters):
        self.src_addr = src_addr
        self.status = status
        self.nwk_addr = nwk_addr
        self.length = length
        self.endpoint = endpoint
        self.profile_id = profile_id
        self.device_id = device_id
        self.device_ver = device_ver
        self.in_clusters = in_clusters
        self.out_clusters = out_clusters

class ZdoActiveEndpointResponse(object):
    """ZDO active endpoint response class"""
    def __init__(self, src_addr, status, nwk_addr, active_eps):
        self.src_addr = src_addr
        self.status = status
        self.nwk_addr = nwk_addr
        self.active_eps = active_eps
