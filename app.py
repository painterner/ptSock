from pt_net import sigHandle, remote,rrmote,local,llocal,mockApi
from pt_crypto import Crypto
from pt_aes import decrypt, encrypt, getKey
import sys,os


if __name__ == "__main__":
    assert(len(sys.argv) > 0)
    role = sys.argv[1]
    host = sys.argv[2]
    assert(role in ['local', 'remote', 'test'])

    LLaddr = {'HOST': '127.0.0.1', 'PORT': 1080}
    Raddr = {'HOST': host, 'PORT': 8390}
    APIaddr = {'HOST': '127.0.0.1', 'PORT': 8391}

    aesKey = getKey()

    netHandle = sigHandle()
    def app(role):
        if(role == 'local'):
            ll = llocal(LLaddr)
            l = local(Raddr)
            # l.setPreConnect([
            #     lambda data: pubKey
            # ])
            ll.setMiddle(l)
            ll.setPipeCallback(
                near={'data':lambda data: encrypt(data,aesKey)},
                far={'data':lambda data: decrypt(data, aesKey)}
            )
            ll.start()
            netHandle.add([ll,l])

        elif(role == 'remote'):
            # crypto = Crypto(512)
            # crypto.newkey()  #保存公钥私钥
            # netKey = crypto.netKey
            # print('netKey:', netKey)

            r = remote(Raddr)
            rr = rrmote()
            r.setMiddle(rr)
            # r.setPreConnect([
            #     lambda data: netKey['pub']
            # ])
            r.setPipeCallback(
                near={'data':lambda data: decrypt(data,aesKey)},
                far={'data':lambda data: encrypt(data, aesKey)}
            )
            r.start()

            netHandle.add([r,rr])

    if(role == 'test'):
        api = mockApi(APIaddr)
        app('remote')
        app('local')
    else:
        app(role)
