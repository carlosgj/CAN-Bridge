import can
import struct
import socket


REMOTE_IP = "192.168.1.22" #Remote computer to send CAN frames to
REMOTE_PORT = 8000 #Remote port to send CAN frames to
LOCAL_IP = "0.0.0.0" #IP to bind to; should usually be 127.0.0.1 or 0.0.0.0
LOCAL_PORT = 8000 #Port on local machine to listen for CAN frames
CAN_IF = "can0" #SocketCAN interface

def prettyprint(binstr):
    return ' '.join(["0x%02x"%ord(x) for x in binstr])

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((LOCAL_IP, LOCAL_PORT))
sock.setblocking(0)

with can.interface.Bus(CAN_IF, bustype='socketcan') as bus:
    while True:
        try:
            message = bus.recv(0.0001)
            if message:
                addrstr = struct.pack('>I', message.arbitration_id)
                datastr = ''.join([chr(x) for x in message.data])
                outstr = addrstr + datastr
                sock.sendto(outstr, (REMOTE_IP, REMOTE_PORT))
                print "[C->N]", prettyprint(outstr)
            instr = ""
            try:
                instr, fromip = sock.recvfrom(12)
            except socket.error as e:
                pass
            if instr:
                addr = struct.unpack('>I', instr[:4])[0]
                data = [ord(x) for x in instr[4:]]
                #print "Data:", ["0x%02x"%x for x in data]
                canmsg = can.Message(arbitration_id=addr, data=data, is_extended_id=True)
                bus.send(canmsg)
                print "[N->C]", canmsg

        except KeyboardInterrupt:
            break

