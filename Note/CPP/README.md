# C-Plus-Plus-Study-Record
Title: variable, memory space and memory address
content: 
1. variable: normal type - int a
             reference type - int& ref_a
             pointer type - int* pointer_a
2. memory space and address:  
var       space      addr
var1       --        xxx1
var2       --        xxx2
var3       --        xxx3

3. relationship:
int a = 3
int& ref_a = a
int* pointer_a = &a

var             space      addr
a, ref_a          3        xxx1     &a == &ref_a
pointer_a       xxx1       xxx2     pointer_a == &a    *pointer_a == a

4. application:
func prototype --
void func1(int& ref_a)
void func2(int* pointer_a)

use --
int a
func1(a)
func2(&a)

## Ways of initializing an object
```
class Entity {
public:
    int x, y;
    
    Entity() : x(0), y(0) { }
    Entity(int x, int y) : x(x), y(y) { }
}

Entity ent1;                //Uses the default constructor, so x=0 and y=0
Entity ent2();              //Uses the default constructor, so x=0 and y=0 (Not sure)
Entity ent3(1, 2);          //Made constructor, so x=1 and y=2
Entity ent4 = Entity();     //Default constructor, so x=0 and y=0
Entity ent5 = Entity(2, 3); //Made constructor, so x=2 and y=3
```
## Inheritance
type | Same Class | Derived Class | Outer Class
--- | --- | --- | ---
*public* | yes | yes | yes
*protected* | yes | yes | no
*private* | yes | no | no

```
#include <iostream>
#include <vector>
#include <math.h>
using namespace std;

class BasePt {
public:
    int indx;
protected:
    double x, y, z;

    BasePt(double _x, double _y, double _z) :x(_x), y(_y), z(_z)
    {
        indx = 0;
        cout << "basePt\n";
    }

    void setIndx(int _indx) {
        indx = _indx;
    }

};

class FeaturePt : public BasePt {
public:
    FeaturePt(double _x, double _y, double _z):BasePt(_x,_y,_z)
    {
        cout << "FeaturePt\n";
    }

    double getDist() {
        return sqrt(pow(x,2)+pow(y,2)+pow(z,2));
    }
};

int main()
{
    FeaturePt pt(1,1,2);
    cout << "pt distance to origin is: " << pt.getDist();
}

```