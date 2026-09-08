# Symbol versioning

All symbol versioning related functionality is guarded by the `ELD_ENABLE_SYMBOL_VERSIONING`
build macro.

## What is symbol versioning?

Symbol versioning lets a single shared library export more than one definition
of the same symbol name, each tagged with a *version*, and lets a client bind
to a specific one. This is how a library can change the behavior of a function
while keeping old binaries working: the old binaries keep resolving to the old
version, and newly linked binaries pick up the new one — all from the same
`.so`, with no SONAME bump.

A versioned symbol name has one of two forms:

- **default** version (`foo@@V2`): satisfies references to both `foo@V2` and
  the plain, unversioned `foo`. There is at most one default version per name;
  it is the version a fresh link picks up when the source just writes `foo`.
- **non-default** version (`foo@V1`): satisfies only the explicit `foo@V1`
  reference. It exists so binaries previously linked against `foo@V1` keep
  resolving to that older definition.

## How to use symbol versioning

A library attaches versions to its symbols in one of two ways: a *version
script*, or `.symver` directives in the source. When a library needs to export
several versions of the *same* name, `.symver` is required.

The example below builds a library `libfoo` that exports both `foo@V1` and the
default `foo@@V2`, then links two executables against it: one that takes the
default (`foo@@V2`) implicitly, and one that explicitly pins `foo@V1`.

**The library.** `.symver` gives each C function a versioned export name, and
the version script declares the version nodes `V1` and `V2`:

```c
// foo.c
__asm__(".symver foo_v1, foo@V1");
int foo_v1() { return 1; }

__asm__(".symver foo_v2, foo@@V2");   // @@ marks the default
int foo_v2() { return 2; }
```

```
// vs.t
V1 { global: foo; };
V2 { global: foo; };
```

```bash
clang -c -fPIC foo.c -o foo.o
ld.eld -m elf_x86_64 -shared --version-script vs.t -o libfoo.so foo.o
```

The dynamic symbol table now carries both versions, and `.gnu.version_d`
defines `V1` and `V2`:

```console
$ llvm-readelf --dyn-syms libfoo.so | grep 'foo@'
     3: 00000000000001f0    11 FUNC    GLOBAL DEFAULT     4 foo@V1
     4: 0000000000000200    11 FUNC    GLOBAL DEFAULT     4 foo@@V2

$ llvm-readelf --version-info libfoo.so
...
Version definition section '.gnu.version_d' contains 3 entries:
  0x0000: Rev: 1  Flags: BASE  Index: 1  Cnt: 1  Name: libfoo.so
  0x0014: Rev: 1  Flags: none  Index: 2  Cnt: 1  Name: V1
  0x0028: Rev: 1  Flags: none  Index: 3  Cnt: 1  Name: V2
```

**Executable using the default (`foo@@V2`).** A plain reference to `foo` binds
to the default version:

```c
// use_default.c
extern int foo();
int main() { return foo(); }
```

```bash
clang -c use_default.c -o use_default.o
ld.eld -m elf_x86_64 -o use_default.out use_default.o libfoo.so
```

```console
$ llvm-readelf -r use_default.out | grep foo
... R_X86_64_JUMP_SLOT  0000000000000000 foo@V2 + 0
```

**Executable pinning `foo@V1`.** A `.symver` on the *reference* forces the
older version:

```c
// use_v1.c
__asm__(".symver foo, foo@V1");
extern int foo();
int main() { return foo(); }
```

```bash
clang -c use_v1.c -o use_v1.o
ld.eld -m elf_x86_64 -o use_v1.out use_v1.o libfoo.so
```

```console
$ llvm-readelf -r use_v1.out | grep foo
... R_X86_64_JUMP_SLOT  0000000000000000 foo@V1 + 0
```

Both executables link against the same `libfoo.so`, but each is bound to a
different definition of `foo` — the loader honors the version recorded in each
executable's `.gnu.version` / `.gnu.version_r` at runtime.

## Symbol resolution of versioned symbols

A versioned symbol is of two types:

- **default** versioned symbol (`bar@@V1`): a default versioned symbol
  satisfies undefined references of both the versioned and
  unversioned references of the symbol. `bar@@V1` definition can satisfy
  undefined references of both `bar@V1` and plain `bar`.
- **non-default** versioned symbol (`bar@V1`): a non-default versioned
  symbol only satisfies undefined references of the versioned references
  of the symbol. `bar@V1` definition can only satisfy undefined references
  of `bar@V1`.

eld supports symbol resolution of versioned symbols by inserting two
symbols for default-versioned symbols into the already-existing symbol resolution
machinery and adding a symbol normalization phase that runs after symbol resolution
to combine the two symbol nodes for the default-versioned symbols into one, if required.

Whenever eld sees a non-default-versioned symbol defintion `bar@V1`, then eld
inserts `bar@V1` to the symbol resolution machinery, and it automatically
gets used to resolve `bar@V1` undefined references.

Here is the interesting part, whenever eld sees a default-versioned symbol
definition `bar@@V1`, then eld inserts two symbols to the symbol resolution
machinery: a canonical symbol `bar@V1` and a non-canonical symbol `bar`.
With this, `bar@@V1` definition resolves undefined references to both
`bar` and `bar@V1`, as it should.

One fundamental rule of versioned-symbol resolution is that, for a default
versioned symbol, both the canonical symbol (`foo@V1`) and the non-canonical
(unversioned symbol `foo`) must resolve to the same definition. Allowing them
to resolve to different symbols is incorrect because, the unversioned
symbol is simply an alias for the versioned symbol (`foo@V1`), and both are
originally the same symbol (`foo@@V1`).

### Why is symbol normalization required?

As we saw above, for a default-versioned symbol definition `bar@@V1`,
eld creates two symbols `bar@V1` and `bar`. Some undefined symbol references
may have resolved to `bar@V1` definition and some may have resolved to `bar`
definition. This is a problem because in reality there is only one symbol
`bar@@V1`. If we keep two symbol nodes per default-versioned symbol definition,
then we will need to also emit both these symbols into the symbol table and
create duplicate GOT/PLT slots for these symbols.

Symbol normalization resolves this duplicate symbol issue by rewriting
all the references to non-canonical symbols (`bar`) into the canonical symbols
(`bar@V1`). A key thing to note here is that we only require the non-canonical
aliases during symbol resolution phase.

LLD does not always normalize the symbols and thus creates duplicate GOT/PLT slots for the same
symbol when a default versioned symbol is accessed as both plain unversioned reference
and versioned reference.

Reproducer:

```bash
#!/usr/bin/env bash

cat >1.c <<\EOF
__asm__(".symver foo1,foo@@V1");
int foo1() {
  return 1;
}
EOF

cat >vs.t <<\EOF
V1 {
  global:
    foo;
};
EOF

cat >main.c <<\EOF
#include <stdio.h>

int foo();

__asm__(".symver foov1, foo@V1");
int foov1();

int main() {
  int u = foo() + foov1();
  printf("u: %d\n",u);
  return 0;
}
EOF

clang-20 -o 1.o 1.c -c -fPIC
clang-20 -o main.o main.c -c -fPIC

LDs=(ld.eld ld.lld ld.bfd)
SFs=(eld lld bfd)

for i in "${!SFs[@]}"; do
  ${LDs[$i]} -o lib1.${SFs[$i]}.so 1.o -shared --version-script vs.t
  clang-20 -o main.${SFs[$i]}.out main.o lib1.${SFs[$i]}.so --ld-path=$(which ${LDs[$i]})
  echo "${SFs[$i]}:"
  llvm-readelf -r main.${SFs[$i]}.out | grep foo
  echo ""
done
```

Output:

```bash
eld:
0000000000002230  0000000700000007 R_X86_64_JUMP_SLOT     0000000000000000 foo@V1 + 0

lld:
0000000000003a58  0000000600000007 R_X86_64_JUMP_SLOT     0000000000000000 foo@V1 + 0
0000000000003a68  0000000800000007 R_X86_64_JUMP_SLOT     0000000000000000 foo@V1 + 0

bfd:
0000000000004008  0000000500000007 R_X86_64_JUMP_SLOT     0000000000000000 foo@V1 + 0
```

### Versioned symbols symbol-resolution examples

Symbol resolution of versioned-symbols is largely the same as
non-versioned symbols. However, there are (corner) cases that
may seem surprising. Here we will see some examples of symbol resolution
of versioned symbols. We will also note differences from GNU ld (2.46.50)
and lld (22.0) wherever relevant.

In these examples (A) and (B) are simply used to differentiate symbols and
to avoid any confusion when referring to them. Please note that (A) and (B)
does not mean that the symbols come from different input files.

The order matters in these examples, (A) `bar@@V1`, (B) `bar@V2`, means
that the linker first sees `bar@@V1` and then sees `bar@V2`.

The symbols originates from regular object files unstated otherwise.

1) (A) `bar@@V1`, (B) `bar@V1`

multiple definition error.

2) (A) `bar@@V1`, (B) weak `bar@V1`

(A) `bar@@V1` is used to resolve undefined references to `bar@V1` and `bar`.

3) (A) weak `bar@@V1`, (B) `bar@V1`

(B) `bar@V1` is used to resolve undefined references to `bar@V1` and `bar`.

(B) `bar@V1` becomes a default-versioned symbol, and appears as `bar@@V1` in
the dynamic symbol table.

4) (A) weak `bar@@V1`, (B) `bar`

(B) `bar` is used to resolve undefined references to `bar@V1` and `bar`.

(B) `bar` becomes a default-versioned symbol, and appears as `bar@@V1` in the
dynamic symbol table.

5) (A) weak `bar@@V1`, (B) `bar@@V1`

(B) `bar@@V1` is used to resolve undefined references to `bar@V1` and `bar`.

6) (A) `bar@@V1`, (B) `bar@@V2`

eld and bfd errors out with multiple definition error.

lld incorrectly links correctly. Reproducer:

```bash
#!/usr/bin/env bash

cat >1.c <<\EOF
__asm__(".symver foo1,foo@@V1");
int foo1() {
  return 1;
}

__asm__(".symver foo2,foo@@V2");
int foo2() {
  return 3;
}

__asm__(".symver bar,bar@V2");
int bar() {
  return 5;
}
EOF

cat >main.c <<\EOF
#include <stdio.h>

int foo();
int bar();

int main() {
  int u = foo() + bar();
  printf("u: %d\n",u);
  return 0;
}
EOF

cat >vs.t <<\EOF
V1 {
  global:
    foo;
};

V2 {
  global:
    foo;
};
EOF

clang-20 -o 1.o 1.c -c -fPIC
clang-20 -o main.o main.c -c

LDs=(ld.eld ld.lld ld.bfd)
SFs=(eld lld bfd)

for i in "${!SFs[@]}"; do
  clang-20 -o lib.${SFs[$i]}.so 1.o --ld-path=$(which ${LDs[$i]}) -shared -fPIC -Wl,--version-script,vs.t
done
```

7) (A) weak `bar@@V1`, (B) `bar`, (C) `bar@V1`

multiple definition error.

8) (A) weak `bar@@V1`, (B) weak `bar`, (C) `bar@V1`

(C) `bar@V1` is used to resolve undefined references to both `bar` and `bar@V1`.

9) (A) weak `bar@@V1`, (B) `bar`, and version script that assigns
   `V2` to `bar`.

(B) `bar` becomes a default versioned symbol and appears as `bar@@V1`
in the dynamic symbol table. **There will be no `bar@@V2` in the symbol table!**

reproducer:

```bash
#!/usr/bin/env bash

cat >1.c <<\EOF
__asm__(".symver bar1, bar@@V1");
__attribute__((weak))
int bar1() {
  return 1;
}
EOF

cat >2.c <<\EOF
int bar() {
  return 3;
}
EOF

cat >3.c <<\EOF
int bar();

__asm__(".symver bar3v1, bar@V1");
int bar3v1();

int b() {
  return bar() + bar3v1();
}
EOF

cat >vs.t <<\EOF
V2 {
  global:
    bar;
};

V1 {
  global:
    bar;
};
EOF

cat >main.c <<\EOF
#include <stdio.h>
#define show(x) printf("%s: %d\n", #x, x);

int b();
int bar();

__asm__(".symver bar1, bar@V1");
int bar1();

int b_main() {
  return bar() + bar1();
}

int main() {
 show(b());
 show(b_main());
 return 0;
}
EOF

TARGET="x86_64-linux-gnu"

clang -target ${TARGET} -o 1.o 1.c -c -fPIC
clang -target ${TARGET} -o 2.o 2.c -c -fPIC
clang -target ${TARGET} -o 3.o 3.c -c -fPIC
clang -target ${TARGET} -o main.o main.c -c

LDs=(ld.eld ld.lld ld.bfd)
SFs=(eld lld bfd)

for i in "${!SFs[@]}"; do
  ${LDs[$i]} -o lib12.${SFs[$i]}.so 1.o 2.o 3.o --version-script vs.t -shared
  clang -target ${TARGET} --ld-path=$(which ${LDs[$i]}) -o main.${SFs[$i]}.out main.o lib12.${SFs[$i]}.so
done
```

10) (A) `bar`, (B) weak `bar@@V1`, and version script that assigns
   `V2` to `bar`.

With GNU ld, the dynamic symbol table contains both `bar@@V1` and `bar@@V2`, and
with lld and eld, the dynamic symbol table only contains `bar@@V1`.

Additionally, GNU seems to incorrectly resolves `bar@V1` undefined references to
weak `bar@@V1`, instead of the plain `bar`. LLD and eld correctly behaves here.

Reproducer:

```bash
#!/usr/bin/env bash

cat >1.c <<\EOF
__asm__(".symver bar1, bar@@V1");
__attribute__((weak))
int bar1() {
  return 1;
}

int bar() {
  return 5;
}
EOF

cat >2.c <<\EOF
int baz() {
  return 3;
}
EOF

cat >3.c <<\EOF
int bar();

__asm__(".symver bar3v1, bar@V1");
int bar3v1();

int b() {
  return bar() + bar3v1();
}
EOF

cat >vs.t <<\EOF
V2 {
  global:
    bar;
};

V1 {
  global:
    bar;
};
EOF

cat >main.c <<\EOF
#include <stdio.h>
#define show(x) printf("%s: %d\n", #x, x);

int b();
int bar();

__asm__(".symver bar1, bar@V1");
int bar1();

int b_main() {
  return bar() + bar1();
}

int main() {
 show(b());
 show(b_main());
 return 0;
}
EOF

TARGET="x86_64-linux-gnu"

clang -target ${TARGET} -o 1.o 1.c -c -fPIC
clang -target ${TARGET} -o 2.o 2.c -c -fPIC
clang -target ${TARGET} -o 3.o 3.c -c -fPIC
clang -target ${TARGET} -o main.o main.c -c

LDs=(ld.eld ld.lld ld.bfd)
SFs=(eld lld bfd)

for i in "${!SFs[@]}"; do
  ${LDs[$i]} -o lib12.${SFs[$i]}.so 1.o 2.o 3.o --version-script vs.t -shared
  clang -target ${TARGET} --ld-path=$(which ${LDs[$i]}) -o main.${SFs[$i]}.out main.o lib12.${SFs[$i]}.so
done
```

11) (A) bar, (B) `bar@@V1`, and version script that assigns
    `bar` to the version node `V2`.

With GNU ld, the dynamic symbol table contains both `bar@@V1` and `bar@@V2`, and
with lld, the dynamic symbol table only contains `bar@@V1`.

> [!IMPORTANT]
> eld currently reports multiple definition error.

12) (A) `bar@@V1`, (B) `bar`, and version script that assigns
    `bar` to the version node `V2`.

Multiple definition error.
