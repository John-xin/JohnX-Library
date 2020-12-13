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

