/*rsa.c RSA算法实现*/
#include "crypto.h"
#include <iostream>

/*modexp 二进制平方乘算法函数*/
static Huge modexp(Huge a, Huge b, Huge n)
{
    Huge y;
    /*使用二进制平方乘法计算 pow(a,b) % n*/
    y=1;
    while(b != 0)
    {
        /*对于b中的每个1，累加y*/
        if(b & 1)
            y = (y*a) % n;
        /*对于b中的每一位，计算a的平方*/
        a = (a*a) % n;
        /*准备b中的下一位*/
        b = b>>1;
    }
    return y;
}

/*rsa_encipher RSA算法加密*/
void rsa_encipher(Huge plaintext, Huge *ciphertext, RsaPubkey pubkey)
{
    *ciphertext = modexp(plaintext, pubkey.e, pubkey.n);
    return;
}

/*rsa_decipher RSA算法解密*/
void rsa_decipher(Huge ciphertext, Huge *plaintext, RsaPriKey prikey)
{
    

    *plaintext = modexp(ciphertext, prikey.d, prikey.n);
    return;
}




void check_rsa(RSA rsa){
    
    if(rsa.e == 3){
        int v = (rsa.p-1)*(rsa.q-1) % rsa.e;
        if(v != 0){
            throwError("rsa check error");
        }
    } else{
        throwError("currently only support e equal to 3");
    }

}

#ifdef ASAPP
int main(int argc, char* argv[]) {
    // 通常选择3、17、65、537作为e的值。使用这些值不会对RSA的安全性造成影响，因为解密数据还需要用到私钥。？
    RSA rsa;
    rsa.p=11;
    rsa.q=19;

    MakeRangePrime();

    // d = e-1 mod (p-1)(q-1) 在实践中，可以利用欧几里德算法来计算模乘法逆元。?

    rsa_encipher
}

#endif
