# ELD layout evaluation

## Assignment evaluation

Linker scripts assignments directly influence the layout. For example,
an assignment to the location counter (`.`) decides where to place the next
content.

Forward references (reference-first-then-definition) are allowed in
linker-scripts. They are error-prone, and can make the layout difficult to
understand, but are allowed nonetheless.

When evaluating an expression, symbol value of a linker script symbol depends
upon whether the linker script symbol assignment preceeds the expression getting
evaluated in the linker script. We compute linker script symbols value as follows:

- If the symbol assignment preceeds the expression getting evaluated in the linker script,
  then the symbol value is the current value of the symbol. The current value of the symbol
  is the value of the latest evaluated assignment of the symbol in the evaluation order.

- Otherwise, the symbol value is the final value of the symbol, that is, the value of the
  last assignment of the symbol.

It is implemented by storing source assignment with each symbol node. The symbol node value
is computed as SourceAssignment.value() instead of the symbol.value(). Source assignment
is the last assignment of the symbol for the symbol nodes which have no corresponding preceding
symbol assignment.

The SourceAssignment approach of computing symbol value is especially helpful because during
layout iteration, we have to restart the layout in-between when some core assumption changes,
such as number of segments.

### Assignment levels

A lot of details involving linker script assignment computation depends upon
the assignment level. An assignment is assigned one of the below levels:

- `BeforeSections`
- `AfterInputSectDesc`
- `AfterOutputSection`
- `AfterSections`

Let's understand these levels with the help of an example:

```
u = v; // A1

SECTIONS{
  v = w; // A2
  .out : {
    w = x; // A3
  }
  x = y; // A4
}
y = z; // A5

SECTIONS {
  z = a; // A6
  .another_out : {
    a = b; // A7
  }
  b = c; // A8
}
```

Here we have 8 assignments: A1, A2, A3, A4, A5, A6, A7 and A8.

A1 is `BeforeSections`.
A3, and A7 are `AfterInputSectDesc`.
A2, A4, A6, and A8 are `AfterOutputSection`.
A5 is `AfterSections`

In most of the cases, `AfterOutputSection` and `AfterSections` assignments
needs to be handled similarly. We often use the term post output section assigments
when we need to refer to both of them.

## Layout convergence

The layout may need multiple iterations to converge when there are
forward-references, or when relaxation/trampolines change the input section
sizes.

Here's a simple example that needs multiple layout iterations due to forward-references:

```
SECTIONS {
  u = v; // A1
  .foo : { *(.text.foo) }
  v = 0x100; // A2
  .data : { *(.text.data) }}
  v = 0x300; // A3
}
```

In the first layout evaluation, the assignment `A1` assigns `0` to `u`. However,
the correct assignment value here is `0x300` that is only known once the layout
has been computed.

We compute the layout iteratively until it converges. Here is
a simplified layout computation pseudo-code:

```cpp
constexpr int maxIterations = 4;
bool isLayoutComplete = false;
while (!isLayoutComplete) {
  for (unsigned i = 0; i < maxIterations; ++i>) {
    LayoutSnapshot prevSnap, curSnap;
    prevSnap = captureLayoutSnapshot();
    computeLayout();
    curSnap = captureLayoutSnapshot();
    if (!hasDiverged(prevSnap, curSnap))
      break;
  }
  relaxLayout(isLayoutComplete);
}
```

The layout iteration has an upper-limit of 4, but it is pre-relaxation layout iteration limit.
After each relaxation pass, the layout iteration count is reset to 0. The `relaxLayout` function
sets `isLayoutComplete` to true in the when the relaxation is complete.

