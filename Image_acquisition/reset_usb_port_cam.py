import usb.core
import usb.util

dev = usb.core.find(idVendor=0x8086,idProduct=0x0B07)

try :
	dev.reset()
	usb.util.dispose_resources(dev)
except Exception as e:
	raise e
