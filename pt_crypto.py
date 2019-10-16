
def pt_generate_key():
    import OpenSSL.crypto as cryptor

    pk = cryptor.PKey()

    print(pk._pkey)

    pk.generate_key(cryptor.TYPE_RSA, 512)

    dump = cryptor.dump_publickey(cryptor.FILETYPE_PEM, pk)
    print(dump)
    dump = cryptor.dump_privatekey(cryptor.FILETYPE_PEM, pk)
    print(dump)

# #签名与验证, 但是verify需要用到X509对象作为参数
# signature = sign(pk, 'hello, world!', 'sha1')
# print(signature)
# x509 = X509()
# x509.set_pubkey(pk)
# verify(x509, signature, 'hello, world!', 'sha1')

# #加解密
# #使用cryptograph
# 这是OpenSSL的后端
# from cryptography.hazmat.backends import openssl
# openssl.rsa._RSAPublicKey.encrypt
# openssl.rsa._RSAPrivateKey.decrypt
# # 需要padding, 但是不了解padding理论

## 使用Crypto库
# from Crypto.PublicKey import RSA
# RSA._RSAobj.decrypt
# :attention: this function performs the plain, primitive RSA decryption
#  (*textbook*). In real applications, you always need to use proper
#  cryptographic padding, and you should not directly decrypt data with
#  this method. Failure to do so may lead to security vulnerabilities.
#  It is recommended to use modules
#  `Crypto.Cipher.PKCS1_OAEP` or `Crypto.Cipher.PKCS1_v1_5` instead.

## 使用rsa库
# https://blog.csdn.net/weixin_39726347/article/details/88622758
import rsa
import base64
import json
import time
class Crypto:
    """
        conventions:
            1. 以base64输出加密信息
    """
    def __init__(self,bits):
        self.pub = None
        self.pri = None
        self.pubkey = None
        self.prikey = None
        self.outformat = bytes
        self.decryArrayFlag = True
        self.pubkeyLength = None
        self.prikeyLength = None
        self.bits = bits
    def newkey(self):
        '''
        新建公钥和私钥并保存到本地
        :return:
        '''
        pubkey, privkey = rsa.newkeys(self.bits)
        self.pubkey = pubkey
        self.prikey = privkey
        self.pub = pubkey.save_pkcs1() #以pem格式保存pubkey
        self.pri = privkey.save_pkcs1() #以pem格式保存privkey
        self.pubkeyLength = rsa.common.byte_size(self.pubkey.n)
        print('pub:',self.pub)
        print('pri:',self.pri)
        # with open('./keys/pubkey.pem','w+') as f:
        #     f.write(pub.decode('utf8'))
        # with open('./keys/privkey.pem','w+') as f:
        #     f.write(pri.decode('utf8'))
    @property
    def netKey(self):
        # return base64.encodebytes(self.pub).decode('utf8') ## return strs
        return {
            'pub':base64.encodebytes(self.pub),
            'pri':base64.encodebytes(self.pri)
        }
    @netKey.setter
    def set_netKey(self,v):
        raise Exception('not implemention')
    def setPubkey(self, pubkey):
        if not isinstance(pubkey, bytes):
            pubkey = pubkey.encode('utf8')
        self.pub = pubkey
        self.pubkey = rsa.PublicKey.load_pkcs1(pubkey)
        self.pubkeyLength = rsa.common.byte_size(self.pubkey.n)

    def singleDecrypto(self,crypto_msg ):
        #读取本地私钥
        # with open('./keys/privkey.pem', 'r') as f:
        #     p = f.read()
        # pri = p.encode('utf8')
        pri = self.pri
        if self.prikey is None:
            prikey = rsa.PrivateKey.load_pkcs1(pri)  #pem格式加载私钥
            self.prikey = prikey
        else:
            prikey = self.prikey

        # # 读取加密文件
        # with open('./keys/msg.txt', 'r') as f:
        #     crypto_msg = f.read()
        
        # base64解码
        if not isinstance(crypto_msg, bytes):
            crypto_msg = crypto_msg.encode('utf8')
        crypto_msg = base64.decodebytes(crypto_msg)

        decrypto_msg = rsa.decrypt(crypto_msg,prikey)  #私钥解密
        return decrypto_msg

    

    def singleEncrypto(self,msg):
        if not isinstance(msg, bytes):
            msg = msg.encode('utf8')
        # with open('./keys/pubkey.pem', 'r') as f:
        #     p = f.read()
        # pub = p.encode('utf8')

        pub = self.pub

        if self.pubkey is None:
            pubkey = rsa.PublicKey.load_pkcs1(pub)  #pem格式加载公钥,返回pkcs
            self.pubkey = pubkey
        else:
            pubkey = self.pubkey

        crypto = rsa.encrypt(msg,pub_key=pubkey) # 使用PKCS加密给定的消息,返回类型bytes

        #对于保存，网络传输，打印不乱码，需要通base64编码进行转换；
        # base64编解码能把一些无法直接用文件本信息编码的二进制数据，转换成常规的二进制数据。

        crypto_msg = crypto
        # if not self.arrayFlag:
        crypto_msg = base64.encodebytes(crypto)  #加密后的文本信息msg
        # if self.format != bytes:
        #     crypto_msg = crypto_msg.decode('utf8')
        
        # 保存加密后的信息到本地
        # with open('./keys/msg.txt', 'w+') as f:
        #     f.write(crypto_msg)
        return crypto_msg
    def split(self,msg):
        msgs = []
        for i in range(0, len(msg), self.pubkeyLength-11):
            msgs.append(msg[i:i+self.pubkeyLength-11])
        return msgs

    def decrypto(self,crypto_msg):
        '''
        私钥解密msg文件
        :return:
        '''
        if self.decryArrayFlag:
            crypto_msg = base64.decodebytes(crypto_msg).decode('utf8')
            crypto_msg = json.loads(crypto_msg)
            lst = []
            for msg in crypto_msg:
                msg = self.singleDecrypto(msg)
                lst.append(msg)
            output = b''.join(lst)
        else:
            output = self.singleDecrypto(crypto_msg)
        if self.outformat != bytes:
            output = output.decode('utf8')
        # print('de:', output)
        return output

    def encrypto(self,msg):
        '''
        用公钥加密msg
        :return:
        '''
        if(isinstance(msg,(tuple,list))):
            assert(isinstance(msg,(list,tuple)))
            msgs = msg
            jsonList = []
            for msg in msgs:
                assert(len(msg) <= self.pubkeyLength-11)
                msg = self.singleEncrypto(msg)
                msg = msg.decode('utf8')
                jsonList.append(msg)
            
            encry_msg = json.dumps(jsonList).encode('utf8')
            encry_msg = base64.encodebytes(encry_msg)
        else:
            keylength = self.pubkeyLength-11
            if(len(msg) > keylength):
                msgList = self.split(msg)
                # print(msgList)
                # exit(1)
                return self.encrypto(msgList)

            encry_msg = self.encrypto([msg]) 
        # print('en:',encry_msg)
        return encry_msg
if __name__ == "__main__":
    crypto = Crypto(512)
    crypto.newkey()  #保存公钥私钥
    crypto.outformat = str
    crypto.decryArrayFlag = True
    
    print('n:', crypto.pubkey.n)
    keylength = crypto.pubkeyLength
    print('keylength:',keylength)

    print('start trans')
    timeA = time.time()
    for i in range(100):
        # uncomment this to test speed of base64
        # inputs = 'okay'*200 + str(i)
        # inputs = inputs.encode('utf8')
        # inputs = base64.encodebytes(inputs)
        # inputs = base64.decodebytes(inputs)
        # inputs = inputs.decode('utf8')
        # continue

        inputs = '你好'*200
        inputs = inputs.encode('utf8')
        msg0 = crypto.encrypto(inputs)  #使用公钥加密信息`
        msg = msg0
        # print('en length:', len(msg))
        demsg = crypto.decrypto(msg)  # 使用私钥解密信息

        if crypto.outformat == bytes:
            print('last:', demsg.decode('utf8'))

    timeA = time.time() - timeA
    print('cusume time:', timeA, 'speed: {} KB/s'.format(len(msg)*100/timeA * 0.001))

# for i in range(100):
#     inputs = 'okay'*200

# 256--> 1.37s
# 512--> 3.06s
# 1024--> 6.45s
