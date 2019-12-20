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
    # print('bs', bs)
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
        raise Exception('data is impossible for less than', bs)
        # return data
    unpad = lambda s : s[0:-s[-1]]
    iv = data[:bs]
    cipher = AES.new(password, AES.MODE_CBC, iv)
    print('data', len(data))
    data = cipher.decrypt(data[bs:])
    data  = unpad(data)
    data = base64.decodebytes( data )
    # data = data.encode('utf8')

    return data

def getKey():
    return '78f40f2c57eee727a4be179049cecf87'

if __name__ == '__main__':

    data = "你好"
    data = b'okay'*100
    password = '78f40f2c57eee727a4be179049cecf87' #16,24,32位长的密码


    encrypt_data = encrypt(data, password)
    print('encrypt_data:', encrypt_data)

    data = b'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\n0TkM'
    # data = b'iSah7KniLHo+AMGkRbgD0O0KXUUpIED34HCMWbJVCJrNcVI1fbpkkgV7D/2KYIvdHuTfZoApsyE9\nhqJtn3gE0Yp7gkFC0fb7Muksnbf4Ew3pOzC2IXOz7lpXR9B4LRy9nYMBTXYEweWq2aZPXRpCHL7O\nEhArUnh/UD3QGdSaynWVVB8bCy5Fp7M9TwUAR1YPn1my54VzlpZzzWPeHNXaFLI7KaUMhs7as1Xi\n7bSKeGilxQC7QgApS5b6GjGuMcXGkTxlJPn4SfnOvhf4ep7dIZYljvieDRlJoPmcxGUWL3EVxFWN\nuu9HGp1xDY+5NoXtJ9NXJozNQGemj0ulEoETz6IZ4Rv4a8Ac2eoT8XHOtG8d7TZiy0VMpCMSWImg\nts3kQhD92H2Zk4oKb0csH+caV4TCDOQh2FiKQ8d28NouVFsigTpmF7tP4Vm9M4nAjsDOPAeCmOOv\nI9HDdeWDDBMcOGfXw57ZiRghnJD+qLSTatcLy7AmZ5bCkgW2qU2qUnex2nrkzINSIyReYsXadwCn\nyqP8qr57zm4+63S29BkuFcOO9FxicebM8kQhO9akd5yLGjPZRIfQ9nzX27lD1HdDXmwQJV4wlGEk\nn7G3Rs4Y+EEj+vrIDM8YoqN0RhY6tnblx1fK6xqcNcG5cVrS1/Z9+Mw3QDAnZSkpDp7QjS3t6fQ6\nuorYzq9jUwdizjazGmO2t+UkfDDYFSE0HPfZvLH49zx3yHBuq8zFB6xYHDSlJaNdNzX0/DH7AUy+\nDWgK+I59cGqWaEh/CZv5gOkWQEVDlXF/KsoEbMm6xD8jpc3xY0lJ9kppBR/RUu1Q4Engh8rL2t4m\nmAjIH50SqOQEk09r5rmUtPf2Q/6C22e1AufpR9ALQrAF8gfFmjI+ztDdaJb57tyGGM5pghm+Nbv4\njXbyZ4gibibSb+qEGpdmS6cheUYUrLkPPfzJVSihCKhOCEYPAqHUPsupw9/5aBUT7Uh/MwiDIwwd\nrP0iJwtejDB/vIuR3zRFiuhRvcEokn/JvXI834jtCWdb/4reFEtknD/gyA/m2FXn8bqejh0qvNIq\nkNf3NT0S2KIzm3TW5HpgQkX7naQ55b80TVQyhVWMKsBbfw==\n'
    # data = base64.encodebytes(data)
    # data = base64.decodebytes(data)``
    # 使用这个测试decrypt_data = decrypt(data, password)
    # 远程部署时测试curl www.163.com 时返回加密后data为这个，解密失败(异常: Input strings must be a multiple of 16 in length), 本地测试却是正常的 ?
    print(len(data))

    # decrypt_data = decrypt(encrypt_data, password)
    decrypt_data = decrypt(data, password)
    decrypt_data = decrypt_data.decode('utf8')
    print('decrypt_data:', decrypt_data)
