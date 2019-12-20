#-*-coding:utf-8-*-

from ecc.encoding import *
from ecc.eccrypt import *
import ecc.ecdsa as ecdsa
import hashlib as hashlib
from ecc.SecurityViolationException import *

class Key:

    # --- KEY SETUP ------------------------------------------------------------

    def __init__(self, public_key, private_key = None):
        '''Create a Key(pair) from numeric keys.'''
        self._pub = public_key
        self._priv = private_key
        self._fingerprint = {}
        self._id = None

    @staticmethod
    def generate(bits):
        '''Generate a new ECDSA keypair'''
        return Key(*ecdsa.keypair(bits))

    # --- BINARY REPRESENTATION ------------------------------------------------

    def encode(self, include_private = False):
        '''Returns a strict binary representation of this Key'''
        e = Encoder().int(self.keyid(), 8)
        e.int(self._pub[0], 2).point(self._pub[1], 2)
        if include_private and self._priv:
            e.long(self._priv[1], 2)
        else:
            e.long(0, 2)
        return e.out()

    def compress(self):
        '''Returns a compact public key representation'''
        

    @staticmethod
    def decode(s):
        '''Constructs a new Key object from its binary representation'''
        kid, ksize, pub, priv = Decoder(s).int(8).int(2).point(2).long(2).out()
        k = Key((ksize, pub), (ksize, priv) if priv else None)
        if kid == k.keyid():
            return k
        else:
            raise ValueError("Invalid Key ID")

    # --- IDENTIFICATION AND VALIDATION ----------------------------------------

    def private(self):
        '''Checks whether Key object contains private key'''
        return bool(self._priv)

    def validate(self):
        '''Checks key validity'''
        if ecdsa.validate_public_key(self._pub):
            if self._priv:          # ? validate and match private key
                return ecdsa.validate_private_key(self._priv) and \
                       ecdsa.match_keys(self._pub, self._priv)
            else:
                return True         # : everything valid
        else:
            return False

    def fingerprint(self, as_hex = True, hashfunc = 'sha1'):
        '''Get the public key fingerprint'''
        if hashfunc in self._fingerprint:
            return self._fingerprint[hashfunc] if not as_hex else \
                   self._fingerprint[hashfunc].encode("hex")
        else:
            h = hashlib.new(hashfunc, enc_point(self._pub[1]))
            d = h.digest()
            self._fingerprint[hashfunc] = d
            return d.encode("hex") if as_hex else d

    def keyid(self):
        '''Get a short, unique identifier'''
        if not self._id:
            self._id = dec_long(self.fingerprint(False, 'sha1')[:8])
        return self._id

    # --- DIGITAL SIGNATURES ---------------------------------------------------

    def sign(self, data, hashfunc = 'sha256'):
        '''Sign data using the specified hash function'''
        if self._priv:
            h = dec_long(hashlib.new(hashfunc, data).digest())
            s = ecdsa.sign(h, self._priv)
            return enc_point(s)
        else:
            raise AttributeError("Private key needed for signing.")

    def verify(self, data, sig, hashfunc = 'sha256'):
        '''Verify the signature of data using the specified hash function'''
        h = dec_long(hashlib.new(hashfunc, data).digest())
        s = dec_point(sig)
        return ecdsa.verify(h, s, self._pub)

    # --- HYBRID ENCRYPTION ----------------------------------------------------

    def encrypt(self, data):
        '''Encrypt a message using this public key'''
        ctext, mkey = encrypt(data, self._pub)
        return Encoder().point(mkey).str(ctext, 4).out()

    def decrypt(self, data):
        '''Decrypt an encrypted message using this private key'''
        mkey, ctext = Decoder(data).point().str(4).out()
        return decrypt(ctext, mkey, self._priv)
        
    # --- AUTHENTICATED ENCRYPTION ---------------------------------------------

    def auth_encrypt(self, data, receiver):
        '''Sign and encrypt a message'''
        sgn = self.sign(data)
        ctext, mkey = encrypt(data, receiver._pub)
        return Encoder().point(mkey).str(ctext, 4).str(sgn, 2).out()

    def auth_decrypt(self, data, source):
        '''Decrypt and verify a message'''
        mkey, ctext, sgn = Decoder(data).point().str(4).str(2).out()
        text = decrypt(ctext, mkey, self._priv)
        if source.verify(text, sgn):
            return text
        else:
            raise SecurityViolationException("Invalid Signature")


if __name__ == "__main__":

    import time

    def test_overhead():
        print ("sender", "receiver", "+bytes", "+enctime", "+dectime")
        for s in [192, 224, 256, 384, 521]:
            sender = Key.generate(s)
            for r in [192, 224, 256, 384, 521]:
                receiver = Key.generate(r)
                t = time.time()
                data = "你好"*10000
                e = sender.auth_encrypt(data, receiver)
                t1 = time.time() - t
                t = time.time()
                text= receiver.auth_decrypt(e, sender)
                # print(text)
                t2 = time.time() - t
                print (s, r, len(e), t1, t2)

    test_overhead()
                
                
    
