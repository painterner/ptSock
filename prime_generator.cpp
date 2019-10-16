#include <iostream>
#include <math.h>
#include "util.h"
#include "crypto.h"
using namespace std;

bool IsPrime(int num)
{
	if(num < 2)
		return false;
	if(num == 2)
		return true;
		
	if(num % 2 == 0)
		return false;
		
	for(int i = 3; i <= sqrt(num); ++i)
	{
		if(num % i == 0)
			return false;
	}
	return true;
}
 
//https://blog.csdn.net/moses1213/article/details/52074886
//用来生成1到n之间的素数。
void MakePrime(int n)
{
	for(int i = 1; i < n + 1; ++i)
	{
		if(IsPrime(i))
			cout << i << " ";
	}
	cout << endl;
}

void MakeRangePrime(Huge n, Huge m)
{
    Huge a = min(n,m);
    Huge b = max(n,m);
    assert( b >= a);
    for(Huge i=a; i<=b; i++){
        if(IsPrime(i))
            cout << i << " ";
    }
    cout << endl;
}

#ifdef APP_GENERATOR
int main(int argc, char* argv[])
{
    MakePrime(100);
    MakeRangePrime(100, 200);

}
#endif

