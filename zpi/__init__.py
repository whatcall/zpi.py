'''
    zpi.py - TI CC2530 ZNP API support package
    
    @author:    tianj@sunsunlighting.com
    @copyright: SunSun Lighting 2012
    @note:      This package implements API support for TI CC2530 ZNP module.
                It exposes all ZNP interfaces to easy access API functions.   
'''
from frame import *
from command import *
from zpi2 import *

def set_debug(onoff = True):
    '''debug feature switch'''
    import zpi2
    import znp
    zpi2.set_debug(onoff)
    znp.set_debug(onoff)
