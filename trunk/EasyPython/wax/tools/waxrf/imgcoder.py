#-------------------------------------------------------
# imgcoder.py
#   Purpose: To encode/decode images for XRC
#    Author: Jason Gedge
#
#   TODO:
#       - Consider better encoding/decoding
#-------------------------------------------------------


import base64


def DecodeImage(data):
    """ Decode an image from WaxRF data. """
    #return base64.b64decode(data)
    return base64.decodestring(data)

def EncodeImage(data):
    """ Encode an image for WaxRF. """
    #return base64.b64encode(data)
    return base64.encodestring(data)

def EncodeImageFile(fname):
    """ Encode an image from a file. """
    data = file(fname, 'rb').read()
    return EncodeImage(data)
