'''
work with bits and bytes packing/unpacking
'''
import struct

def get_bit(byte,position):
    '''
    return bit at position in byte (from 0)
    '''
    return byte & 1 << position != 0


def set_bit(value, index, bit):
  """Set the index: bit of value to 1 if bit is true, else to 0, and return the new value."""
  mask = 1 << index   # Compute mask, an integer with just bit 'index' set.
  value &= ~mask          # Clear the bit indicated by the mask (if x is False)
  if bit:
    value |= mask         # If x was True, set the bit indicated by the mask.
  return value 

def bit_list_2_int(bitList: list[bool] | list[int]) -> int:
    '''
    takes bit list of 2 bytes [True, True, False,...] [1,0,0,1...] 
    returns integer
    '''
    result=0
    for i,bit in enumerate(bitList):
        result+=bit*2**i
    return result

def int_2_bit_list(i: int) -> list[bool]:
    '''
    i - integer 0-65535
    return [1,1,1,0,0,.....] len 16
    '''
    # return [True if b=='1' else False for b in reversed(bin(i)[2:].zfill(16))]
    return [1 if b=='1' else 0 for b in reversed(bin(i)[2:].zfill(16))]

def convert_int16_AB2BA (value:int)->int:
    bytes = int_2_bit_list(value)
    b1 = bytes[:7]
    b2 = bytes[7:]
    return bit_list_2_int(b2.extend(b1))

def pack_int32_to_CDAB(value: int)-> list:
    bytes = int_2_bit_list(value)
    A = bytes[:7]
    B = bytes[7:13]
    C = bytes[13:20]
    D = bytes[20:28]
    return [bit_list_2_int(C+D), bit_list_2_int(A+B)]

def pack_int32_to_ABCD(value: int)-> list:
    bytes = int_2_bit_list(value)
    A = bytes[:7]
    B = bytes[7:13]
    C = bytes[13:20]
    D = bytes[20:28]
    return [bit_list_2_int(A+B), bit_list_2_int(C+D)]



def unpack_CDAB_to_int32(word_list: list)-> int: #??? long integer
    ...


def float_pack_2_ABCD(f: float)-> list:
    '''
    pack float to 2 words HIGH LOW  \n
    return [HIGH_16_byte, LOW_16_byte]
    '''
    A, B, C, D = [i for i in struct.pack('>f',f)]
    return [B+A*256, D+C*256]
    # return [b[i+1]*256+b[i] for i in range(0,len(b),2)]


def float_pack_2_CDAB(f: float)-> list:
    '''
    pack float to 2 words  list [LOW_16bit, HIGH_16bit] \n
    return [LOW_16_byte, HIGH_16_byte]
    '''
    # b=[i for i in struct.pack('<f',f)]
    A, B, C, D  = [i for i in struct.pack('<f',f)]
    return [A+B*256, C+D*256 ]
    # return [b[i+1]*256+b[i] for i in range(0,len(b),2)]

 
def ABCD_unpack_2_float(two_words: list,round_count: int=0) -> float:
    '''
    unpack list [LOW_16bit, HIGH_16bit] \n
    return [LOW_16_byte, HIGH_16_byte] \n
    round to round_count if exist
    '''
    try:
        hex_data=two_words[0].to_bytes(2,byteorder='big')+two_words[1].to_bytes(2,byteorder='big')
        result=struct.unpack('>f', hex_data)[0]
        if round_count:
            return round(result, round_count)
        else:
            return result
    except Exception:
        raise ValueError(f"unpackCDABToFloat: can't unpack {two_words}")


def CDAB_unpack_2_float(two_words: list[int], round_count: int=0) -> float:
    '''
    unpack list [LOW_16bit, HIGH_16bit] \n
    return [LOW_16_byte, HIGH_16_byte] \n
    round to round_count if exist
    '''
    try:
        hex_data=two_words[1].to_bytes(2,byteorder='big')+two_words[0].to_bytes(2,byteorder='big')
        result=struct.unpack('>f', hex_data)[0]
        if round_count:
            return round(result, round_count)
        else:
            return result
    except Exception:
        raise ValueError(f"unpackCDABToFloat: can't unpack {two_words}")


unpackABCDToFloat=ABCD_unpack_2_float
unpackCDABToFloat=CDAB_unpack_2_float
packFloatToCDAB=float_pack_2_CDAB
packFloatToABCD=float_pack_2_ABCD
getBit=get_bit
setBit=set_bit
int2BitList=int_2_bit_list
bitList2int=bit_list_2_int

def tests():
    a=4.01
    print (f'testing pack/unpackCDABToFloat: {a== unpackCDABToFloat(packFloatToCDAB(a),2)}')

if __name__ == "__main__":
    d=float_pack_2_CDAB(2.5)
    print (d)
    a=CDAB_unpack_2_float(d)
    print (a)
    d1=float_pack_2_ABCD(2.5)
    print (d1)
    a1=ABCD_unpack_2_float(d1)
    print (a1)
    # print (getBit(655,0))

    # tests()
    # r=packFloatToCDAB(29.01)
    # print (r)
    # r=packFloatToCDAB(4.01)
    # print (r)
    # f=unpackCDABToFloat(r,2)
    # print(f)
