/*encrypt.h*/
#ifndef CRYPTO_H
#define CRYPTO_H
#include <iostream>
#include "util.h"
#include <stdio.h>
#include <stdlib.h>
#include <gmp.h>

/*在一个安全实现中，Huge 最少要400位10进制数字*/
typedef unsigned long Huge; 

/*为RSA公钥定义一个数据结构*/
typedef struct RsaPubKey_
{
    Huge e;
    Huge n;
}RsaPubkey;

/*为RSA私钥定义一个数据结构*/
typedef struct RsaPriKey_
{
    Huge d;
    Huge n;
}RsaPriKey;

struct RSA
{
    int p;
    int q;
    const int e=3;
    int d;
};

struct BIGNUM {
    char value[256];
    // char t[256];
    mpz_t shadow;
    // mpz_t temp;
    BIGNUM() {
        for(auto &v: value){
            int r = rand() % 10;
            v = r+0x30;  
        }
        // mpz_t temp;
        // mpz_init(temp);
        // mpz_set_str(temp, t, 10);
        mpz_t shadow;
        mpz_init(shadow);
        mpz_set_str(shadow, value, 10);
    };
    ~BIGNUM() {
        // mpz_clear(temp);
        mpz_clear(shadow);
    }

    BIGNUM operator+(BIGNUM & e){
        mpz_add(shadow, shadow, e.shadow);
    }
    BIGNUM operator-(BIGNUM & e){
        mpz_sub(shadow, shadow, e.shadow);
    }
    BIGNUM operator / (){

    }


    int test(void){

        char a[1000];
        char b[1000];

        scanf("%s", a);
        scanf("%s", b);
        mpz_t x;
        mpz_t y;
        mpz_t result;
        mpz_init(x);
        mpz_init(y);
        mpz_init(result);
        //mpz_set_str(x, "7612058254738945", 10);
        //mpz_set_str(y, "9263591128439081", 10);
        //10代表十进制
        mpz_set_str(x, a, 10);
        mpz_set_str(y, b, 10);
        mpz_add(result, x, y);
        gmp_printf("\n    %Zd\n+\n    %Zd\n--------------------\n%Zd\n\n", x, y, result);
        mpz_sub(result, x, y);
        gmp_printf("\n    %Zd\n-\n    %Zd\n--------------------\n%Zd\n\n", x, y, result);
        mpz_mul(result, x, y);
        gmp_printf("\n    %Zd\n*\n    %Zd\n--------------------\n%Zd\n\n", x, y, result);
        mpz_fdiv_q(result, x, y);
        gmp_printf("\n    %Zd\n/\n    %Zd\n--------------------\n%Zd\n\n", x, y, result);
        mpz_fdiv_r(result, x, y);
        gmp_printf("remainder:\t%Zd\n\n\n", result);
        /* free used memory释放内存*/
        mpz_clear(x);
        mpz_clear(y);
        mpz_clear(result);
    }

};

void MakeRangePrime(Huge n, Huge m);


/*函数声明*/
void des_encipher(const unsigned char *plaintext, unsigned char *ciphertext, const unsigned char *key);
void des_decipher(const unsigned char *ciphertext, unsigned char *plaintext, const unsigned char *key);
void rsa_encipher(Huge plaintext, Huge *ciphertext, RsaPubkey pubkey);
void rsa_decipher(Huge ciphertext,Huge *plaintext, RsaPriKey prikey);

#endif // ENCRYPT_H
