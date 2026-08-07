typedef __UINTPTR_TYPE__ uintptr_t;
void foo(void);
int main(void) { return (int)(uintptr_t)foo; }
