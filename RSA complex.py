import random
import math

# Цветовой дизайн консоли
NORMAL = "\x1b[39m"
RED    = "\x1b[91m"
GREEN  = "\x1b[92m"
YELLOW = "\x1b[93m"
BLUE   = "\x1b[94m"


def N(z: complex):
    return int(z.real*z.real + z.imag*z.imag)

def gcd_r(a, b):
    if b > a: a, b = b, a
    
    q = 1
    r = 1
    s1 = 1
    s2 = 0
    t1 = 0
    t2 = 1
    
    
    while r != 0:
        q = round(a / b)
        r = a - b*q
        s1, s2 = s2, s1 - q*s2
        t1, t2 = t2, t1 - q*t2
        a, b = b, r
    return (s1, t1, a)

def gcd(a, b):
    if N(b) > N(a): a, b = b, a
    """
    Finds the GCD of two Gaussian integers a + bi and c + di.
    """
    q = complex(1, 1)
    r = complex(1, 1)
    s1 = complex(1, 0)
    s2 = complex(0, 0)
    t1 = complex(0, 0)
    t2 = complex(1, 0)

    while N(r) != 0:
        q = a / b
        q = complex(round(q.real), round(q.imag))
        r = a - b*q
        s1, s2 = s2, s1 - q*s2
        t1, t2 = t2, t1 - q*t2
        a, b = b, r
    return (s1, t1, a)

def is_prime(z):
    if type(z) == complex:
        n = N(z)
    elif type(z) == int:
        n = z
    else: return False
    if n <= 1:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True


def generate_keys(n: int, log = False):
    flag_1, flag_2 = True, True
    while (flag_1 or flag_2):
        if flag_1:
            a = random.randrange(int(round(n/10)), n)
            b = random.randrange(int(round(n/10)), n)
            z1 = complex(a, b)
            if is_prime(z1):
                if log: print("z1 -", z1, "  N =", N(z1))
                flag_1 = False
        if flag_2:
            a = random.randrange(1, n)
            b = random.randrange(1, n)
            z2 = complex(a, b)
            if is_prime(z2):
                if log: print("z2 -", z2, "  N =", N(z2))
                flag_2 = False
    z12 = z1*z2
    if log: print("z12 -", z12, "  N =", N(z12))
    phi = (N(z1) - 1)*(N(z2) - 1)
    if log: print("phi -", phi)
    d = 0
    while (d != 1):
        e = random.randrange(1, phi)
        s, t ,d = gcd_r(e, phi)
    if log: print("e -", e)
    if log: print ("D, S, T >> ", d, s, t, " -> s*phi + t*e =", s*phi + t*e)
    if t < 0 : t = t + phi
    return (z12, e), (z12, t)

BIT_DENCITY = 11

def decode_binary_string(s):
    return ''.join(chr(int(s[i*BIT_DENCITY:i*BIT_DENCITY+BIT_DENCITY],2)) for i in range(len(s)//BIT_DENCITY))

def encode_binary_string(s):
    return ''.join([bin(ord(c))[2:].rjust(BIT_DENCITY,'0') for c in s])


def binToGauss(line: str):
    line = line[::-1]
    z = complex(0, 0)
    zi = complex(1, 0)
    for char in line:
        if char == "1": z = z + zi
        zi = zi * (1 + 1j)
    return z

def GaussToBin(z: complex):
    line = ""
    b = 1 + 1j
    while N(z) != 1:
        q = complex(round((z / b).real), round((z / b).imag))
        r = z - q*b
        if N(r) == 0:
            z = q
            line += "0"
        else:
            z = (z - complex(1, 0)) / b
            line += "1"
    line += "1"
    return line[::-1]

def pow_c(a:complex, n:int, mod:complex):
    res = a
    nn = n - 1
    if(N(a) >= N(mod)):
        q = complex(round((a / mod).real), round((a / mod).imag))
        res = a - q * mod
        print(RED + "[ ! ]" + YELLOW + " A > mod inittially, decription will fail" + NORMAL)
    while nn > 0:
        if nn % 2 == 0:
            a = a * a
            nn = nn / 2
            q = complex(round((a / mod).real), round((a / mod).imag))
            a = a - q * mod
        else:
            res = res * a
            nn = nn - 1
            q = complex(round((res / mod).real), round((res / mod).imag))
            res = res - q * mod
    return res
    
def encodeText(m: complex, pubkey):
    n, e = pubkey
    c = pow_c(m, e, n)
    return c

def decodeText(c: complex, privkey):
    n, d = privkey
    m = pow_c(c, d, n)
    return m


print("\n\n\n")

PubKey, PrivKey = generate_keys(10000, False)
print(PubKey, PrivKey)


text = input("Enter the text to encode: ")
chunk_size = 4
chararray = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
if len(chararray[-1]) < chunk_size:
    chararray[-1] += ' ' * (chunk_size - len(chararray[-1]))

print(chararray)
textZ, Z_encode, Z_decode = [], [], []
for l in chararray:
    encoded = encode_binary_string(l)
    # print(encoded)
    l_inZ = binToGauss(encoded)
    textZ.append(l_inZ)
    
print(textZ)

for z in textZ:
    encoded = encodeText(z, PubKey)
    Z_encode.append(encoded)

print("\n\n", Z_encode,"\n\n")

decoded_text = ''
for z in Z_encode:
    decoded = decodeText(z, PrivKey)
    l_fromZ = GaussToBin(decoded)
    if (len(l_fromZ) < BIT_DENCITY * chunk_size):
        i = BIT_DENCITY * chunk_size - len(l_fromZ)
        l_fromZ = "0"*i + l_fromZ
    # print(l_fromZ)
    decoded_text += decode_binary_string(l_fromZ)
    Z_decode.append(decoded)
    
print(Z_decode)    
print(decoded_text)



# print("\n\n\n")
# print(encoded)
# print(decode_binary_string(encoded))