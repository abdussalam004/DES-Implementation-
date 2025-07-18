# DES Tables

InitialP = [
    58,50,42,34,26,18,10,2,
    60,52,44,36,28,20,12,4,
    62,54,46,38,30,22,14,6,
    64,56,48,40,32,24,16,8,
    57,49,41,33,25,17,9,1,
    59,51,43,35,27,19,11,3,
    61,53,45,37,29,21,13,5,
    63,55,47,39,31,23,15,7
]

FinalP = [
    40,8,48,16,56,24,64,32,
    39,7,47,15,55,23,63,31,
    38,6,46,14,54,22,62,30,
    37,5,45,13,53,21,61,29,
    36,4,44,12,52,20,60,28,
    35,3,43,11,51,19,59,27,
    34,2,42,10,50,18,58,26,
    33,1,41,9,49,17,57,25
]

Expansion = [
    32,1,2,3,4,5,
    4,5,6,7,8,9,
    8,9,10,11,12,13,
    12,13,14,15,16,17,
    16,17,18,19,20,21,
    20,21,22,23,24,25,
    24,25,26,27,28,29,
    28,29,30,31,32,1
]

PC1 = [
    57,49,41,33,25,17,9,
    1,58,50,42,34,26,18,
    10,2,59,51,43,35,27,
    19,11,3,60,52,44,36,
    63,55,47,39,31,23,15,
    7,62,54,46,38,30,22,
    14,6,61,53,45,37,29,
    21,13,5,28,20,12,4
]

PC2 = [
    14,17,11,24,1,5,
    3,28,15,6,21,10,
    23,19,12,4,26,8,
    16,7,27,20,13,2,
    41,52,31,37,47,55,
    30,40,51,45,33,48,
    44,49,39,56,34,53,
    46,42,50,36,29,32
]

LeftShifts = [1,1,2,2,2,2,2,2,1,2,2,2,2,2,2,1]

Sbox = [
    [14,4,13,1,2,15,11,8,3,10,6,12,5,9,0,7],
    [0,15,7,4,14,2,13,1,10,6,12,11,9,5,3,8],
    [4,1,14,8,13,6,2,11,15,12,9,7,3,10,5,0],
    [15,12,8,2,4,9,1,7,5,11,3,14,10,0,6,13]
]

# DES utility functions

def str_to_bin(text):
    return [int(bit) for char in text for bit in format(ord(char), '08b')]

def bin_to_str(bits):
    return ''.join(chr(int(''.join(str(b) for b in bits[i:i+8]), 2)) for i in range(0, 64, 8))

def permute(input_bits, table):
    return [input_bits[pos-1] for pos in table]

def xor(bits1, bits2):
    return [a ^ b for a, b in zip(bits1, bits2)]

def shift_left(bits, shifts):
    return bits[shifts:] + bits[:shifts]

def sbox_substitute(bits):
    sOut = []
    for i in range(8):
        block = bits[i*6:i*6+6]
        row = (block[0] << 1) | block[5]
        col = (block[1] << 3) | (block[2] << 2) | (block[3] << 1) | block[4]
        val = Sbox[row % 4][col % 16]
        sOut.extend([(val >> j) & 1 for j in reversed(range(4))])
    return sOut

def generate_subkeys(key_bits):
    key56 = permute(key_bits, PC1)
    C = key56[:28]
    D = key56[28:]
    subkeys = []
    for shift in LeftShifts:
        C = shift_left(C, shift)
        D = shift_left(D, shift)
        combined = C + D
        subkey = permute(combined, PC2)
        subkeys.append(subkey)
    return subkeys

# DES encryption with 16 rounds

def des_encrypt(plaintext, keytext):
    pt_bits = str_to_bin(plaintext)
    key_bits = str_to_bin(keytext)
    key_bits = (key_bits + [0] * (64 - len(key_bits)))[:64]  
    
    ip = permute(pt_bits, InitialP)
    L = ip[:32]
    R = ip[32:]
    
    subkeys = generate_subkeys(key_bits)
    
    for i in range(16):
        RE = permute(R, Expansion)
        RK = xor(RE, subkeys[i])
        sOut = sbox_substitute(RK)
        newR = xor(sOut, L)
        L = R
        R = newR
    
    pre_output = R + L  
    final_bits = permute(pre_output, FinalP)
    
    return bin_to_str(final_bits)

# Test

plaintext = "Daffodil"
keytext = "SECURITY"

ciphertext = des_encrypt(plaintext, keytext)

print("Plaintext :", plaintext)
print("Ciphertext:", ' '.join(f"{ord(c):02X}" for c in ciphertext))
