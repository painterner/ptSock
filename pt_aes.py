# encoding:utf-8
import base64
from Crypto.Cipher import AES
from Crypto import Random
 
def encrypt(data, password):
    if isinstance(data, str):
        data = base64.encodebytes(data.encode('utf8')).decode('utf8')
    elif isinstance(data, bytes):
        data = base64.encodebytes(data).decode('utf8')
    # print('\nencrypt input: ', data)
    bs = AES.block_size
    pad = lambda s: s + (bs - len(s) % bs) * chr(bs - len(s) % bs)
    iv = Random.new().read(bs)
    cipher = AES.new(password, AES.MODE_CBC, iv)
    data = pad(data)
    # print('\nencrypt input: {} \n'.format(data))
    data = cipher.encrypt(data)
    data = iv + data
    # data = base64.b64encode(data)
    data = base64.encodebytes(data)
    # print('\nencrypt output: {} \n'.format(data))
    return data
 
def decrypt(data, password):
    print('\ndecrpy input: {} \n'.format(data))
    # data = base64.b64decode(data)
    data = base64.decodebytes(data)
    bs = AES.block_size
    if len(data) <= bs:
        return data
    unpad = lambda s : s[0:-s[-1]]
    iv = data[:bs]
    cipher = AES.new(password, AES.MODE_CBC, iv)
    data = cipher.decrypt(data[bs:])
    data  = unpad(data)
    data = base64.decodebytes( data )

    return data

def getKey():
    return '78f40f2c57eee727a4be179049cecf87'
 
if __name__ == '__main__':
    data = "你好"
    data = b'okay'*100
    password = '78f40f2c57eee727a4be179049cecf87' #16,24,32位长的密码
    

    encrypt_data = encrypt(data, password)
    print('encrypt_data:', encrypt_data)
     
    decrypt_data = decrypt(encrypt_data, password)
    decrypt_data = decrypt_data.decode('utf8')
    print('decrypt_data:', decrypt_data)