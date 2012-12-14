''' 
    CC2530-ZNP class module 
'''
import struct
import threading
import time

import logging

log = logging.getLogger('drivers.cc2530_zpi.znp')
console = logging.StreamHandler()
formatter = logging.Formatter('[%(asctime)s] %(message)s')
console.setFormatter(formatter)
log.addHandler(console)
log.setLevel(logging.INFO)

from frame import ZnpFrame

def set_debug(onoff):
    if onoff:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)

def _len_calc(x_value, expr = 'x'):
    ''' 
        calculate the len with a customized expression, such as : x*2. 
        x_value must be properly provided
    '''
    x = x_value
    x = x               #prevent 'unused' warning
    return eval(expr)
    
class ThreadQuitException(Exception):
    pass

class CommandFrameException(KeyError):
    pass

    
class Znp(threading.Thread):
    '''
        ZNP class (as Zpi Base) 
        
        ZNP commands are in 4 types: POLL (SPI only), SREQ, AREQ, SRSP.
        SREQ is synchronous request that requires an immediate response.
        AREQ is asynchronous request that with response in callback event or w/o 
            response.
        SRSP is a synchronous response. It's only sent in response to a SREQ 
            command.
    '''
    def __init__(self, ser, callback = None):
        super(Znp, self).__init__()
        self.serial = ser
        self._callback = None
        self._thread_continue = False
        
        if callback:
            self._callback = callback
            self._thread_continue = True
            self.start()
            
    def halt(self, timeout = None):
        '''
            halt the thread
        '''
        if self._callback:
            self._thread_continue = False
            self.join(timeout)
            
    def _write(self, data):
        '''
            write data to serial
        '''
        frame = ZnpFrame(data).output()
        log.debug('TX: %s' % frame.encode('hex'))
        self.serial.write(frame)

        
    def run(self):
        '''
            this method overrides threading.Thread.run() and is automatically 
            called by self.start()
        '''
        rx_data = None
        while True:
            try:
                #self._callback(self.wait_read_frame())
                rx_data = self.wait_read_frame()

                log.debug('RX SRSP/AREQ: %s' % rx_data['id'])  
                log.debug('rx_data: %s' % rx_data)              
                self._callback(rx_data)
            except ThreadQuitException:
                log.info('Znp thread exited.')
                break
            except Exception as e:
                log.warning('Znp:{}'.format(e))
                continue
            
    def _wait_for_frame(self):
        '''
            read from the serial port until a valid ZNP frame arrives. It will 
            then return the binary data contained within the frame
        '''
        frame = ZnpFrame()
        
        while True:
            if self._callback and not self._thread_continue:
                raise ThreadQuitException
            
            if self.serial.inWaiting() == 0:
                time.sleep(0.005)       #5ms polling
                continue
            
            byte = self.serial.read()
            
            if byte != ZnpFrame.SOF:
                continue
            
            # save all following bytes
            if len(byte) == 1:
                #print 'received: SOF'
                frame.fill(byte)
                
            #TODO: how to handle the rx timeout situation if not enough bytes     
            while frame.remaining_bytes() > 0:
                byte = self.serial.read()
                
                if len(byte) == 1:
                    #print 'received: %s' % byte.encode('hex')
                    frame.fill(byte)
                    
            try:
                log.debug('RX: %s' % frame.raw_data.encode('hex'))
                frame.parse()
                
                #ignore empty frames
                if len(frame.data) == 0:
                    log.debug('Empty frame received!')
                    frame = ZnpFrame()
                    continue
                
                return frame
            except ValueError:
                #bad frame, so restart
                log.debug('bad frame received!')
                frame = ZnpFrame()
                
    def _build_frame(self, cmd, **kwargs):
        '''
            this function must be used with a pre-defined dictionary
        '''
        try:
            cmd_spec = self.znp_commands[cmd]
        except AttributeError:
            raise NotImplementedError('ZNP Commands not found!')
        
        packet = b''
        
        #save a temporary {field_name: value} dictionary for variable 
        #lengh calculating
        field_dict = {}
        
        for field in cmd_spec:
            #some difference for pyxbee, we have variable length for some 
            #mid-fields, a (relative field name, expression) us  used to 
            #solve this issue 
            field_len_expr = field['len']
            field_len = None
            if isinstance(field_len_expr, int):
                field_len = int(field_len_expr)
            elif isinstance(field_len_expr, tuple):
                #try to get relative field value and calculate
                try:
                    relative_len = struct.unpack('B', field_dict[field_len_expr[0]])[0]
                    field_len = _len_calc(relative_len, field_len_expr[1])
                except:
                    raise ValueError('Length expression calculation failed.')
            else:
                pass # len is None   
                
            try:
                data = kwargs[field['name']]
            except KeyError:  
                #is no field specified in kwargs, assign default value if existed
 
                                
                if field_len is not None:
                    default_value = field['default']
                    if default_value:
                        data = default_value
                    else:
                        raise KeyError(
                            'The expected field %s of length %d was not provided' 
                            % (field['name'], field_len))
                else:
                    data = None     
             
            #check len spec if len specified        
            if field_len and len(data) != field_len:
                raise ValueError(
                    "The data provided for '%s' was not %d bytes long"\
                    % (field['name'], field_len))
            
            field_dict[field['name']] = data  #update the dict
                
            if data:
                packet += data
                
        log.debug('TX packet: %s' % packet.encode('hex'))        
        return packet
        
    def _split_response(self, data):
        '''
            convert data received into a dictionary
        '''
        packet_id = data[0:2] #CMD0,CMD1
        
        #print 'Received packet id: %s' % packet_id.encode('hex')
        #print repr(packet_id)
        
        try:
            packet = self.znp_responses[packet_id]
        except AttributeError:
            raise NotImplementedError('Cannot find API response specifications!')
        except KeyError:
            #check to see if response can be found in tx commands list
            for cmd_name, cmd in list(self.znp_commands.items()):
                if cmd[0]['default'] == data[0:1]:
                    raise CommandFrameException('''Incomming frame with id %s 
                        looks like a command frame of type '%s' but with wrong 
                        data''' % (data[0], cmd_name))
            raise KeyError('Unrecognized response packet with cmd: %s' % data[0:2].encode('hex'))
        
        index = 2  #start from 2 because we have 2 command bytes
        
        #pre-store the signature of the incoming packet
        info = {'id': packet['name'], 'cmd0': packet_id[0], 'cmd1': packet_id[1]}        
        packet_spec = packet['structure']
        
        for field in packet_spec:
            field_len_expr = field['len']   #get field len expression
            field_len = None                #real number value of field len
            if field_len_expr == 'null_terminated':
                field_data = b''
                
                while data[index:index+1] != b'\x00':
                    field_data += data[index:index+1]
                    index += 1
                
                index += 1   
                info[field['name']] = field_data
            elif field_len_expr is not None:
                if isinstance(field_len_expr, int):  #explicit integer num
                    field_len = int(field_len_expr)
                elif isinstance(field_len_expr, tuple):  #need evaluation
                    #try to get relative field value and calculate
                    try:
                        relative_len = struct.unpack('B', info[field_len_expr[0]])[0]
                        field_len = _len_calc(relative_len, field_len_expr[1])
                    except:
                        raise ValueError('Length expression calculation failed.')
                else:
                    raise ValueError('Invalid value specified for len field!')
                
                if index + field_len > len(data):
                    raise ValueError('Response packet was shorter than expected!') 
                
                field_data = data[index:index + field_len]
                info[field['name']] = field_data
                
                index += field_len
            else: #if None specified, the all rest data will be retrieved.
                field_data = data[index:]
                
                if field_data:
                    info[field['name']] = field_data
                    index += len(field_data)
                break
            
        if index < len(data):
            log.error ('Data: %s' % data.encode('hex'))
            raise ValueError('Response packet is longer than expected.'
                'Expected: %d, got: %d bytes. ''' % (index, len(data)))
            
        # Apply parsing rules if any exist
        if 'parsing' in packet:
            for parse_rule in packet['parsing']:
                # Only apply a rule if it is relevant (raw data is available)
                if parse_rule[0] in info:
                    # Apply the parse function to the indicated field and 
                    # replace the raw data with the result
                    info[parse_rule[0]] = parse_rule[1](self, info)                                                                                   
            
        return info
            
    def send(self, cmd, **kwargs):
        '''
            send data to radio
        '''
        self._write(self._build_frame(cmd, **kwargs))
        log.debug('TX SREQ/AREQ: %s' % cmd)
        
    def wait_read_frame(self):
        '''
            wait for reading a valid frame from radio
        '''
        frame = self._wait_for_frame()
        return self._split_response(frame.data)
    
    def __getattr__(self, name):
        '''
            
        '''
        if name == 'znp_commands':
            raise NotImplementedError('ZNP command specification could not be found.')
        