class flags(object):
    DPUSH = 0x01
    KCASTLE = 0x02
    QCASTLE = 0x04
    CAPTURE = 0x08
    EP = 0x10


def new(frm, to, cpiece=-1, flags=0x00, cr=0X0F):
    return (frm, to, cpiece, flags, cr)
