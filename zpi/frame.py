"""
    CC2530-ZNP frame process module
"""

import struct

class ZnpFrame(object):
    """ 
        represent a frame of data to be sent to or received from an CC2530-ZNP 
        device
    """
    #Start of frame
    SOF = b'\xfe'
    
    #Commands
    #    Format: Cmd0 (b7~5: type, b4~0: subsystem), cmd1 (b7~0: ID)
    CMD_POLL = 0  #only available for SPI transport
    CMD_SREQ = 1
    CMD_AREQ = 2
    CMD_SRSP = 3
    
    SUB_RPC_ERR = 0
    SUB_SYS = 1
    SUB_AF = 4
    SUB_ZDO = 5
    SUB_SAPI = 6
    SUB_UTIL = 7
    
    SYS_RESET_REQ = 0x00
    SYS_RESET_IND = 0x80
    SYS_VERSION = 0x02 
    
    
    #SAPI
    ZB_APP_REG_REQ = 0x0A
    
    #AF
    AF_DATA_REQ = 0x01
    
    LEN_SOF = 1
    LEN_LENGTH = 1
    LEN_CMD = 2
    LEN_FCS = 1
    LEN_NOTDATA = LEN_SOF + LEN_LENGTH + LEN_CMD + LEN_FCS
    
    def __init__(self, data = b''):
        self.data = data
        self.raw_data = b''
        
    def checksum(self):
        """
            FCS byte is calculated with XOR method.
            
            FCS: contain all bytes before FCS excluding SOF
        """
        if self.data is not None and len(self.data) > 0:
            fcs = self.len_data()  #first XOR with len byte
            for i in range(0, len(self.data)):
                fcs = fcs ^ struct.unpack('B', self.data[i])[0]
            return struct.pack('B',fcs)
        else:
            raise ValueError('self.data is empty!')
        
    def verify(self, chksum):
        """
            verify the data with a given chksum
        """
        
        return self.checksum() == chksum
    
    def len_data(self):
        """
            count number of bytes contained in data
            CMD0,CMD1 are not included
        """
        if len(self.data) >= ZnpFrame.LEN_CMD:
            count = len(self.data) - ZnpFrame.LEN_CMD
            return count
        else:
            raise ValueError('Data content is not long enough!')
        
    def len_bytes(self):
        """
            count number of bytes contained in data and return as byte
            CMD0,CMD1 are not included
        """
        return struct.pack('<B', self.len_data())

    def output(self):
        """
        
        """
        data = self.len_bytes() + self.data + self.checksum()
        
        return ZnpFrame.SOF + data
    
    @staticmethod
    def escaped():
        """
        
        """
        raise NotImplementedError
    
    def fill(self, byte):
        """
            adds the given byte to this frame
        """
        self.raw_data += byte
        
    def remaining_bytes(self):
        """
            calculate the remaining byte 
        """
        #LEN:1, Command: 2, Data:0~250, FCS:1
        remaining = 4   #the default minimal value (no fcs)
        
        if len(self.raw_data) >= 2:   #2nd byte is byte
            raw_len = self.raw_data[1:2]
            data_len = struct.unpack('>B', raw_len)[0]
            
            remaining += data_len
            
            remaining += 1 #add FCS byte length
            
        return remaining - len(self.raw_data)
            
    def parse(self):
        """
            parse raw_data:
                - get the data content (len byte not included)
                - verify the checksum
            I sense the value is not telli
        """
        if len(self.raw_data) < 4:
            raise ValueError("""parse() may only be called on a frame containing 
                at least 3 bytes of raw data (see fill())""")
        
        #1st byte is the length
        raw_len = self.raw_data[1:2]
        data_len = struct.unpack('>B', raw_len)[0]
        
        #read the data    
        data  =self.raw_data[2:(2 + data_len + ZnpFrame.LEN_CMD)]
        chksum = self.raw_data[-1]
        
        
        #verify checksum
        self.data = data
        if not self.verify(chksum):
            raise ValueError('Invalid checksum!')
        