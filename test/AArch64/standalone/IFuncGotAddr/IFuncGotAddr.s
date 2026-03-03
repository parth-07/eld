#---IFuncGotAddr.s--------------------- Executable --------------------#
#BEGIN_COMMENT
# When code takes the address of an IFUNC symbol through the GOT in a static
# executable (via R_AARCH64_ADR_GOT_PAGE + R_AARCH64_LD64_GOT_LO12_NC), the
# GOT entry must contain the address of the PLT entry, not the IFUNC resolver.
# The PLT entry correctly indirects through the IRELATIVE-resolved GOT.PLT
# slot, so callers that load the function pointer from the GOT and then call
# through it will reach the real implementation rather than the resolver.
#
# This is a regression test for a bug where storing the IFUNC resolver address
# in the regular GOT entry caused silent memory corruption: code that loaded
# the address (e.g., to use memcpy as a function pointer) would invoke the
# resolver instead of the actual implementation, appearing to succeed but never
# actually performing the operation.
#END_COMMENT
#START_TEST

# RUN: rm -rf %t && split-file %s %t && cd %t
# RUN: %llvm-mc -filetype=obj -triple=aarch64 def.s -o def.o
# RUN: %llvm-mc -filetype=obj -triple=aarch64 use.s -o use.o
# RUN: %link %linkopts -march aarch64 def.o use.o -o out --section-start .text=0x1000

## Verify an IRELATIVE relocation exists for the IFUNC resolver.
# RUN: llvm-readobj -r out | %filecheck --check-prefix=RELOCS %s

## Verify relevant sections exist.
# RUN: %readelf -S -W out | %filecheck --check-prefix=SECTIONS %s

## The GOT entry (.got) for myfunc must contain the PLT entry address, not the
## resolver address.  With --section-start .text=0x1000, the IFUNC resolver
## lives at 0x1008.  If the linker incorrectly places the resolver address in
## the GOT, the hex dump would contain 0x1008 in little-endian (08100000
## 00000000).  With the fix, the GOT instead holds the PLT entry address which
## is below .text.
# RUN: %readelf -x .got out | %filecheck --check-prefix=GOT %s

# RELOCS: R_AARCH64_IRELATIVE - 0x1008

# SECTIONS: .rela.plt
# SECTIONS: .plt
# SECTIONS: .got
# SECTIONS: .got.plt

## The .got hex dump must NOT contain the resolver address (0x1008 in LE).
## The buggy behavior stored the resolver here; the fix stores the PLT address.
# GOT-NOT: 08100000 00000000

#END_TEST

#--- def.s
// Define an IFUNC symbol whose resolver returns the address of the
// actual implementation.

  .text

// The real implementation.
  .type impl, @function
impl:
  add w0, w0, #1
  ret
  .size impl, .-impl

// The resolver: returns &impl.
  .type resolve_myfunc, @function
resolve_myfunc:
  adrp x0, impl
  add  x0, x0, :lo12:impl
  ret
  .size resolve_myfunc, .-resolve_myfunc

// Declare myfunc as an IFUNC whose resolver is resolve_myfunc.
  .globl myfunc
  .type  myfunc, @gnu_indirect_function
  .set   myfunc, resolve_myfunc

#--- use.s
// Take the address of an IFUNC symbol through the GOT
// (R_AARCH64_ADR_GOT_PAGE + R_AARCH64_LD64_GOT_LO12_NC)
// and also call it directly (R_AARCH64_CALL26 through PLT).

  .text
  .globl _start
  .type  _start, @function
_start:
  // Load &myfunc from GOT -- generates R_AARCH64_ADR_GOT_PAGE +
  // R_AARCH64_LD64_GOT_LO12_NC.  This is the code path that was buggy:
  // the GOT entry must hold the PLT address, not the resolver address.
  adrp x8, :got:myfunc
  ldr  x8, [x8, :got_lo12:myfunc]

  // Call myfunc through PLT -- generates R_AARCH64_CALL26.
  bl   myfunc

  ret
  .size _start, .-_start
