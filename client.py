# EXAMPLE IMPLEMENTATION on ETHEREUM: https://kovan.etherscan.io/address/0x23cacafb1f32c62b805b14fac3417f1e1e3fec98
# pk = (13671745300223455622296976647036122779409479348541974397577710233068369091353, 13911240)
# sk = 13671745300223455622296976647036122779053175926061888065608023302499601004900
import random 
from timeit import timeit
from gmpy2 import invert as gmpy2invert
modinv = lambda x,y: int(gmpy2invert(x,y))
from Crypto.Hash.keccak import Keccak_Hash
keccak256 = lambda preimage: Keccak_Hash(preimage, digest_bytes=32, update_after_digest=False) # the REAL keccak256
eth_pack = lambda x: x.to_bytes(32, 'big')

class VDF: # y = x^(2^Time) mod RSA-N
    # Time constants to help
    Time_1s = 2**16 + 2**15 + 2**14 + 2**10 + 2**7 + 2**6 + 2**4 + 7
    Time_10s = 10*Time_1s
    Time_1m = 6*Time_10s

    # SETUP
    def TrapSetup(Lambda, Time):
        sk, pk = RSA.Setup(Lambda)
        (Totient, d), (N, e) = sk, pk
        PublicParameters, Trap = (N, Time), Totient
        return PublicParameters, Trap

    def Setup_Wes18(Lambda, Time): # this is the unknown group order setup
        return
        return PublicParameters

    # GENERATE input
    def Gen(PublicParameters, Time): # potential plug into blockchain, to hash/randomize the input
        return
        return x, Time

    # EVAL
    def Eval(PublicParameters, x):
        N, Time = PublicParameters
        y = x
        for _ in range(Time):
            y = pow(y,2,N)
        return y

    def TrapEval(PublicParameters, Trap, x):
        (N, Time), Totient = PublicParameters, Trap
        exponent = pow(2, Time, Totient)
        y = pow(x, exponent, N)
        return y

    def Eval_Wes18(PublicParameters, x):
        y = VDF.Eval(PublicParameters, x)
        (N, Time) = PublicParameters

        # long-division algorithm
        pi, residue = 1, 1
        Challenge = VDF.HPrime(N,Time,x,y)
        for _ in range(Time):
            bit = 2*residue // Challenge
            residue = 2*residue % Challenge
            pi = (pi**2 * x**bit) % N
        return y, pi

    def TrapEval_Wes18(PublicParameters, Trap, x):
        y = VDF.TrapEval(PublicParameters, Trap, x)
        (N, Time), Totient = PublicParameters, Trap
        Challenge = VDF.HPrime(N,Time,x,y)
        residue = pow(2, Time, Challenge)
        exponent = ((pow(2, Time, Totient) - residue) * modinv(Challenge, Totient)) % Totient
        pi = pow(x, exponent, N)
        return y,pi

    # VERIFY
    def Verify_Wes18(PublicParameters,x,y,pi):
        (N, Time) = PublicParameters
        Challenge = VDF.HPrime(N,Time,x,y)
        residue = pow(2, Time, Challenge)
        return y == (pow(pi, Challenge, N) * pow(x, residue, N)) % N

    # FiatShamir Challenge 256bits
    def HPrime(_N, _Time, _x, _y):
        # due to solidity limitations i had to limit primes to 256 bits
        # due to performance issues i reduced it to 256-3
        p = int(keccak256(eth_pack(_N)+eth_pack(_Time)+eth_pack(_x)+eth_pack(_y)).hexdigest(), 16)>>3
        if p%2 == 0:
            p = p+1
        while True:
            if Primes.CheckProbablePrime(p):
                RandomProbablePrime = p
                return RandomProbablePrime
            p = p+2

class RSA:
    def Setup(Lambda):
        p, q = Primes.GetProbablePrime(Lambda//2), Primes.GetProbablePrime(Lambda//2)
        while p==q:
            q = Primes.GetProbablePrime(Lambda//2)
        N = p*q
        Totient = (p-1)*(q-1) # group order
        e = 65537 
        d = modinv(e, Totient)
        SecretKey, PublicKey = (Totient, d), (N, e)
        return SecretKey, PublicKey

class Primes:
    FIRST_256_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503, 509, 521, 523, 541, 547, 557, 563, 569, 571, 577, 587, 593, 599, 601, 607, 613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691, 701, 709, 719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797, 809, 811, 821, 823, 827, 829, 839, 853, 857, 859, 863, 877, 881, 883, 887, 907, 911, 919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997, 1009, 1013, 1019, 1021, 1031, 1033, 1039, 1049, 1051, 1061, 1063, 1069, 1087, 1091, 1093, 1097, 1103, 1109, 1117, 1123, 1129, 1151, 1153, 1163, 1171, 1181, 1187, 1193, 1201, 1213, 1217, 1223, 1229, 1231, 1237, 1249, 1259, 1277, 1279, 1283, 1289, 1291, 1297, 1301, 1303, 1307, 1319, 1321, 1327, 1361, 1367, 1373, 1381, 1399, 1409, 1423, 1427, 1429, 1433, 1439, 1447, 1451, 1453, 1459, 1471, 1481, 1483, 1487, 1489, 1493, 1499, 1511, 1523, 1531, 1543, 1549, 1553, 1559, 1567, 1571, 1579, 1583, 1597, 1601, 1607, 1609, 1613, 1619]

    def Check_MillerRabin(p, tests): # error=1/4^tests
        assert(p>0)
        if p in {1,2,3}:
            return True
        if p%2==0:
            return False

        # factorize n-1 = 2^s * r, r is odd
        even, s, r = p-1, 0, 1
        while even%2 == 0:
            even = even//2
            s = s+1
        r=even

        # do the tests
        for _ in range(tests):
            a = random.randint(2, p-2)
            y = pow(a,r,p)
            if y != 1 and y != p-1:
                j = 1
                while j <= s-1 and y != p-1:
                    y = pow(y,2,p)
                    if y == 1:
                        return False
                    j = j+1
                if y != p-1:
                    return False
        return True

    def CheckProbablePrime(p):
        # trial division is faster than Miller-Rabin
        for x in Primes.FIRST_256_PRIMES:
            if p%x == 0:
                if p == x:
                    return True
                else:
                    return False
        else:
            # final check with Miller-Rabin
            return Primes.Check_MillerRabin(p, 20) # switch to 256 for increased accuracy

    def GetProbablePrime(Lambda):
        while True:
            # generate a candidate
            p = random.getrandbits(Lambda)
            if p%2 == 0:
                continue

            # check candidate
            if Primes.CheckProbablePrime(p):
                return p

def performance(TestTime, PrecisionRounds):
    pk, sk = VDF.TrapSetup(1024, TestTime)
    x = 1337
    y, pi = VDF.TrapEval_Wes18(pk, sk, x)
    precisionrounds = PrecisionRounds
    tot = timeit(lambda: VDF.Verify_Wes18(pk, x, y, pi), number = precisionrounds)
    print(f'avg {tot/precisionrounds:.4f} seconds (total {tot:.4f}s)')

#pk, sk = VDF.TrapSetup(256, VDF.Time_1s*120) 
#x = 1337
#y, pi = VDF.Eval_Wes18(pk,x)
#print(VDF.Verify_Wes18(pk, x, y, pi))
