static void foo_impl(void) {
}

static void *resolve_foo(void) {
  return &foo_impl;
}

/* This line makes foo a GNU indirect function. */
asm (".type foo, %gnu_indirect_function");

void *foo(void) {
  return resolve_foo();
}
