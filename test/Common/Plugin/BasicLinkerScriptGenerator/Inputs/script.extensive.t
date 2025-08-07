LINKER_PLUGIN("BasicLinkerScriptGenerator", "BasicLinkerScriptGenerator")

ENTRY("_start")

SECTIONS {
  ".foo" (0x1000) : { *(.text.foo) }
  . = 0x2000;
  .bar : { *(.text.bar) }
}