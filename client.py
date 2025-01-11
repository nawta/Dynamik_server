import sys
import zmq
import time

def start_client():
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5557")

    try:
        while True:
            print("Enter message:")
            message = sys.stdin.readline()
            socket.send_string(message)
            sec_before = time.time()

            recv_message = socket.recv_string()
            print("Receive message = %s" % recv_message)
            sec_after = time.time()
            print("time [sec] = %s" % (sec_after - sec_before))

            print("num of input tokens = {0}".format(len(message.split())))
            print("num of completion tokens = {0}".format(len(recv_message.split())))
            print("---")
    except KeyboardInterrupt:
        socket.close()
        context.destroy()

if __name__ == "__main__":
    start_client()
