SECTIONS {
  .foo : { *(.text.foo) }
  .data : { *(.data*) }
  .bar : { *(.text.bar) }
}

