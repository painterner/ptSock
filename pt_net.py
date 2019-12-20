import socket
import threading
import time
import signal
from http.server import BaseHTTPRequestHandler
from io import BytesIO
from shadowsocks import asyncdns, eventloop

##      llocal - local ==== remote - rrmote
##      ll   -   l   ====   r   -   rr
##     line0  line1      line2     line3   

socket.getaddrinfo('0.0.0.0', None, 0, 0, 0,0)
"""Resolve host and port into list of address info entries.

Translate the host/port argument into a sequence of 5-tuples that contain
all the necessary arguments for creating a socket connected to that service.
host is a domain name, a string representation of an IPv4/v6 address or
None. port is a string service name such as 'http', a numeric port number or
None. By passing None as the value of host and port, you can pass NULL to
the underlying C API.

The family, type and proto arguments can be optionally specified in order to
narrow the list of addresses returned. Passing zero as a value for each of
these arguments selects the full range of results.
"""

BUFFER_SIZE = 64*1024

class HTTPRequest(BaseHTTPRequestHandler):
    def __init__(self, request_text):
        self.rfile = BytesIO(request_text)
        self.raw_requestline = self.rfile.readline()
        self.error_code = self.error_message = None
        self.parse_request()

    def send_error(self, code, message):
        self.error_code = code
        self.error_message = message

def parse(data):
    bytesData = data
    data = HTTPRequest(data)
    # data = json.loads(data)
    print('receive data: ', data.headers['host'], 'error_code:', data.error_code)
    sr = data.headers['host'].split(':')
    print('split:', sr)
    if(len(sr) > 1):
        addr = (sr[0], int(sr[1]))
    else:
        # addr = socket.getaddrinfo(data.headers['host'], 'http', 0, 0, 0, 0)[0][4]
        addr = socket.getaddrinfo(data.headers['host'], 'http', socket.AF_INET, socket.SOCK_STREAM, 0, 0)[0][4]
    if('http'):
        returnData = bytesData
    
    print('addr:', addr)

    return {
        'addr': addr, 
        'data': returnData
    }
# def unparse(addr, data):
#     return addr + '-' + data

class sHandle(threading.Thread):
    def __init__(self,HOST,PORT,dataLen, role=None, mode='pipe', debug=False):
        threading.Thread.__init__(self)
        self.HOST = HOST
        self.PORT = PORT
        self.frameCount = 0
        self.dataLen = dataLen
        self.middle = None
        self.role = role
        self.sock = socket.socket(type=socket.SOCK_STREAM)
        self.runFlag = True
        self.keep_alive = True
        self.preList = []
        self.pipeCallBack={
            "near": {'data': lambda data: data, 'state':True,'msg': None},
            "far": {'data': lambda data: data, 'state':True,'msg': None}
        }
        self.internet = False
        self.mode = mode ## 'pipe', 'echo'
        self.debug = debug
        self.flag_sendLengthInd = False
    def getSock(self):
        return self.sock
    def shutdown(self):
        # close()releases the resource associated with a connection but does not necessarily 
        # close the connection immediately. If you want to close the connection in a timely fashion, 
        # callshutdown() beforeclose().
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()
        except:
            pass
        print('shutdown')
        self.runFlag = False
    def setMiddle(self, middle):
        self.middle = middle
    def setMiddleAddr(self, HOST, PORT):
        self.middle.setAddr(HOST, PORT)
    def setkeepAlive(self, boolv):
        self.keep_alive = boolv
    def keepAlive(self):
        return self.keep_alive
    def setPreConnect(self, lst):
        assert isinstance(lst, (list, tuple))
        self.preList=lst
    def preConnect(self,data):
        if len(self.preList) == 0:
            return [data,False]
        func = self.preList.pop(0)
        data = func(data)
        return [data, True]
    def setPipeCallback(self,near=None,far=None):
        if near is not None:
            self.pipeCallBack['near'].update(near)
        if far is not None:
            self.pipeCallBack['far'].update(far)
        
    def run(self):       
        # with self.sock as s:
        # s = self.sock
        print('will bind at', (self.HOST,self.PORT))
        ## already in use 的原因与解决方法: https://blog.csdn.net/zhzhzh090/article/details/85308911
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.HOST,self.PORT))
        self.sock.listen(2)
        while True:
            try:
                conn,addr = self.sock.accept()  # 测试如果accept过程中close(),依然会already use, 所以直接改成非阻塞。
            except:
                break
            self.curConn = conn
            with conn:
                while True:
                    self.frameCount = self.frameCount + 1
                    print(addr,self.frameCount)
                    # data = conn.recv(self.dataLen,socket.MSG_WAITALL)
                    data = conn.recv(self.dataLen)
                    data, preFlag = self.preConnect(data)
                    if self.debug: print('recv', data)
                    if not data: break
                    if(not preFlag and self.mode !='echo'):
                        
                        #if not data: break
                        transData = self.pipeCallBack['near']
                        data = transData['data'](data)
                        if(not transData['state']):
                            data = transData['msg']
                        else:
                            if(self.middle is not None):
                                if (self.middle.waitAddr or self.internet):
                                    self.setMiddleAddr(*parse(data)['addr'])
                                print(data)
                                data = self.middle.send_and_echo( data )
                                if not data: break
                        # print('\n back \n')
                        transData = self.pipeCallBack['far']
                        data = transData['data'](data)
                        if(not transData['state']):
                            data = transData['msg']
                    # print('data', data)
                    if self.flag_sendLengthInd:
                        data = len(data).to_bytes(8, 'little') + data
                    conn.sendall(data)
                    if(not self.keepAlive()):
                        conn.close()
                        break
            if(not self.runFlag):
                break
        print('listener exited')
    def __call__(self,data):
        pass

class cHandle(threading.Thread):
    def __init__(self, HOST=None, PORT=None, dataLen=1024):
        threading.Thread.__init__(self)
        self.waitAddr = True
        self.dataLen = dataLen
        self.runFlag = True
        self.flag_recvLoop = False

        # self.sock = socket.socket()
        self.sock = None
        self.setAddr(HOST,PORT)
        
    def getSock(self):
        return self.sock
    def shutdown(self):
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()
        except:
            pass
        self.runFlag = False
    def setAddr(self,HOST, PORT):
        self.HOST = HOST
        self.PORT = PORT
        if(self.HOST is not None and self.PORT is not None):
            self.waitAddr = False
            self.close()
            self.connect()
            # self.start()
    def sendall(self, data):
        print('cHandle sendall', data)
        self.sock.sendall(data)
    def sockSend(self, data):
        self.sock.sendall(data)
    def recvLoop(self):
        dl = self.sock.recv(8)
        print('recv loop dl0', dl)
        dl = int.from_bytes(dl, 'little')
        print('recv loop dl1', dl)
        E = b''
        i = 0
        while dl > 0:
            d = self.sock.recv(dl)     
            dl = dl-len(d)
            E += d
            print('recv loop',i,len(d),len(E))
            i = i+1
        return E
        
    def send_and_echo(self, data):
        self.sendall(data)
        if self.flag_recvLoop:  ## 接受数据的某些位置定义需要接受的大小，以便兼容大数据接受。
            data = self.recvLoop()
        else:
            data = self.sock.recv(self.dataLen)
        return data
    def close(self):
        if self.sock:
            self.sock.close()
    def connect(self):
        self.sock = socket.socket()
        self.sock.connect((self.HOST, self.PORT))
    def run(self):
        while True:
            if(not self.runFlag):
                return
            time.sleep(0.2)

config = {
    "ports": ['http', 'https']
}

def llocal(LL):
    # socket.getaddrinfo('0.0.0.0', None, 0, 0, 0,0)
    th = sHandle(LL['HOST'],LL['PORT'],BUFFER_SIZE)
    th.setkeepAlive(False)
    return th

def local(R):
    c = cHandle(R['HOST'] ,R['PORT'], dataLen=BUFFER_SIZE)
    c.flag_recvLoop = True
    return c

def remote(R):
    th = sHandle(R['HOST'] ,R['PORT'],BUFFER_SIZE)
    th.internet = True
    th.flag_sendLengthInd = True
    return th

def rrmote():
    c = cHandle(dataLen=BUFFER_SIZE)
    def sendall(data):
        r = parse(data)
        c.sockSend(r['data'])
    c.sendall = sendall
    return c

def mockApi(addr):
    th = sHandle(addr['HOST'], addr['PORT'], BUFFER_SIZE, mode='echo', debug=True)
    th.start()
    return th

class sigHandle:
    def __init__(self):
        self.models = []
        self.net_signalHandle()
    def add(self, models):
        for m in models:
            if m not in self.models:
                self.models.append(m)
    def net_signalHandle(self):
        def impl(signum, frame):
            if(signum == signal.SIGINT):
                print('shutdown all socks')
                for s in self.models:
                    s.shutdown()
                for s in self.models:
                    try:
                        s.join()
                        print('joined')
                    except:
                        ## 如果是早就退出了的话当然会unjoin(资源都没了怎么join)
                        print('unjoined')
                        continue
                exit(signum)
        signal.signal(signal.SIGINT, impl)

if __name__ == "__main__":
    LLaddr = {'HOST': '127.0.0.1', 'PORT': 1081}
    Raddr = {'HOST': '127.0.0.1', 'PORT': 8390}
    APIaddr = {'HOST': '127.0.0.1', 'PORT': 8391}

    api = mockApi(APIaddr)
    print('mockapi address', APIaddr)

    r = remote(Raddr)
    rr = rrmote()
    r.setMiddle(rr)
    r.start()

    ll = llocal(LLaddr)
    l = local(Raddr)
    ll.setMiddle(l)
    ll.start()

    sigHandle().add([l, ll, r, rr, api])
    
