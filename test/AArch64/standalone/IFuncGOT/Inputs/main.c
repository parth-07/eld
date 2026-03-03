extern void *foo();

int main() {
  // Take address of IFUNC symbol - generates PC-relative relocations
  void *foop = foo;
  // Use the pointer to avoid optimization
  return (foop != 0) ? 0 : 1;
}
