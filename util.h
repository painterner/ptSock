#ifndef UTIL_h
#define UTIL_h

#include<iostream>
using namespace std;

void throwError(char *msg){
    std::cout<< "error: "<<msg<<'\n';
    exit(-1);
}

void assert(bool v) {
    if(!v){
        std::cout<< "assert error: "<<'\n';
        exit(-1);
    }
}

#endif