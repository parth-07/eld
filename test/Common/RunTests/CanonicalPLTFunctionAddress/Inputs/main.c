#include <stdio.h>

int foo(void);
void *foo_addr(void);

int main(void) {
  void *main_addr = (void *)foo;
  void *dso_addr = foo_addr();
  if (main_addr != dso_addr) {
    printf("not equal %p %p\n", main_addr, dso_addr);
    return 1;
  }
  puts("equal");
  return 0;
}
