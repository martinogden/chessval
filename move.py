class flags(object):
	DPUSH = 0x01
	KCASTLE = 0x02
	QCASTLE = 0x03
	CAPTURE = 0x04
	EP = 0x05


def new(frm, to, cpiece=-1, flags=0x00):
	return (frm, to, cpiece, flags)
