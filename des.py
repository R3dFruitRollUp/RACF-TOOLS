import Crypto
import sys
from Crypto.Cipher import DES

class DesCrypt:
    ''' Turn Debugging On '''
    DEBUG=False

    ''' Class variables for:
          dc_user = User ID
          dc_pwd  = User's password
          dc_hash = Generated DES encrypted hash '''
    dc_user =""
    dc_encuser = ""
    dc_pwd  =""
    dc_hash = bytearray()

    ''' Initialize Class (user / password if provided) '''
    def __init__(self,du="",dp=""):
        self.dc_user=du.upper()
        self.dc_pwd=dp
        self.crypt()

    ''' Static array to map ASCII to EBCDIC characters '''
    a2e = [
    0x00,0x01,0x02,0x03,0x37,0x2d,0x2e,0x2f,         #0-8
    0x16,0x05,0x15,0x0b,0x0c,0x0d,0x0e,0x0f,0x10,    #9-18
    0x11,0x12,0x13,0x3c,0x3d,0x32,0x26,0x18,0x19,    #19-28
    0x3f,0x27,0x1c,0x1d,0x1e,0x1f,0x40,0x5a,0x7f,    #29-38
    0x7b,0x5b,0x6c,0x50,0x7d,0x4d,0x5d,0x5c,0x4e,    #39-48
    0x6b,0x60,0x4b,0x61,0xf0,0xf1,0xf2,0xf3,0xf4,    #49-58
    0xf5,0xf6,0xf7,0xf8,0xf9,0x7a,0x5e,0x4c,0x7e,    #59-68
    0x6e,0x6f,0x7c,0xc1,0xc2,0xc3,0xc4,0xc5,0xc6,    #69-78
    0xc7,0xc8,0xc9,0xd1,0xd2,0xd3,0xd4,0xd5,0xd6,    #79-88
    0xd7,0xd8,0xd9,0xe2,0xe3,0xe4,0xe5,0xe6,0xe7,    #89-98
    0xe8,0xe9,0xad,0xe0,0xbd,0x5f,0x6d,0x79,0x81,
    0x82,0x83,0x84,0x85,0x86,0x87,0x88,0x89,0x91,
    0x92,0x93,0x94,0x95,0x96,0x97,0x98,0x99,0xa2,
    0xa3,0xa4,0xa5,0xa6,0xa7,0xa8,0xa9,0xc0,0x4f,
    0xd0,0xa1,0x07,0x20,0x21,0x22,0x23,0x24,0x25,
    0x06,0x17,0x28,0x29,0x2a,0x2b,0x2c,0x09,0x0a,
    0x1b,0x30,0x31,0x1a,0x33,0x34,0x35,0x36,0x08,
    0x38,0x39,0x3a,0x3b,0x04,0x14,0x3e,0xff,0x41,
    0xaa,0x4a,0xb1,0x9f,0xb2,0x6a,0xb5,0xbb,0xb4,
    0x9a,0x8a,0xb0,0xca,0xaf,0xbc,0x90,0x8f,0xea,
    0xfa,0xbe,0xa0,0xb6,0xb3,0x9d,0xda,0x9b,0x8b,
    0xb7,0xb8,0xb9,0xab,0x64,0x65,0x62,0x66,0x63,
    0x67,0x9e,0x68,0x74,0x71,0x72,0x73,0x78,0x75,
    0x76,0x77,0xac,0x69,0xed,0xee,0xeb,0xef,0xec,
    0xbf,0x80,0xfd,0xfe,0xfb,0xfc,0xba,0xae,0x59,
    0x44,0x45,0x42,0x46,0x43,0x47,0x9c,0x48,0x54,
    0x51,0x52,0x53,0x58,0x55,0x56,0x57,0x8c,0x49,
    0xcd,0xce,0xcb,0xcf,0xcc,0xe1,0x70,0xdd,0xde,
    0xdb,0xdc,0x8d,0x8e,0xdf]

    ''' Get parity bit for DES key '''
    def __parityOf(self,int_type):
        p=0
        while(int_type):
            p = ~p
            int_type = int_type & (int_type - 1)
        return p

    ''' Encrypt the USERID with a key generated by using the plaintext
        password provided by the user. 
        **  Note this does not validate the input - but USER IDs must be <= 7 length
            and currently only passwords <= 8 are supported **  '''
    def crypt(self):
        ## ensure upper user id 
        user = self.dc_user
        pwd  = self.dc_pwd

        ## pad the password to 8 chars
        if self.DEBUG: print("DEBUG: Password len {0:d}".format(len(pwd)))
        pwd = pwd + (8 - len(pwd)) * " "

        ## prepare the password (convert to ebcdic and encode)
        ptmp=""
        for i in pwd:
            x=(((self.a2e[ord(i)])^0x55)<<1)&0xff
            ptmp = ptmp + chr(x)

        if self.DEBUG: print("DEBUG: encoded key and ebcdic: " + ptmp.encode('hex'))

        ## add des key parity
        key=""
        for i in range(0,len(ptmp)):
            v= ord(ptmp[i:i+1])
            t=self.__parityOf(v)
            if t==0:
                v=v+1
            key = key + chr(v)

        if self.DEBUG: print("DEBUG: encoded key w parity: " + key.encode('hex'))

        ## encode user id to ebcidic and pad
        euser = user.encode('cp500')              # this is hackish, but works for std chars
        euser = euser + (8 - len(user)) * "\x40"  #\x40 is ebcdic space
        self.dc_encuser = euser

        if self.DEBUG: print ("DEBUG: ebcdic user: " + euser.encode('hex'))

        ## encrypt password with des
        c = DES.new(key, DES.MODE_ECB)
        ct = c.encrypt(euser)

        if self.DEBUG: print("DEBUG: Hash:{0:s}".format(ct.encode('hex')))

        self.dc_hash = bytearray(ct)

        ## decrypt for validation
        # nt = c.decrypt(ct)
        #return [ct.encode('hex'),nt==euser]

    ''' Return the hash hex formatted '''
    def getHexHash(self):
        return str(self.dc_hash).encode('hex')

    ''' Return the hash in byte format '''
    def getHash(self):
        return self.dc_hash

    ''' Set the user id (or change it) '''
    def getEncUser(self):
        return self.dc_encuser

    ''' Set the user id (or change it) '''
    def setUser(self, su_user):
        self.dc_user = su_user.upper()
        if self.DEBUG: print("DEBUG: User Id set to {0:s}".format(su_user))

    ''' Set the user id (or change it) '''
    def setPassword(self, su_password):
        self.dc_pwd = su_password
        if self.DEBUG: print("DEBUG: password set to {0:s}".format(su_password))


##  End Class
