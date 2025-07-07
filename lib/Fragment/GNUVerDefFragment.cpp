#include "eld/Fragment/GNUVerDefFragment.h"
#include "eld/Core/Module.h"
#include "eld/Diagnostics/DiagnosticEngine.h"
#include "llvm/Object/ELF.h"
#include <cstdint>

using namespace eld;

GNUVerDefFragment::GNUVerDefFragment(ELFSection *S)
    : Fragment(Fragment::Type::GNUVerNeed, S) {}

eld::Expected<void> GNUVerDefFragment::emit(MemoryRegion &Mr, Module &M) {
  // uint8_t *Buf = Mr.begin() + getOffset(M.getConfig().getDiagEngine());
  // bool Is32Bits = M.getConfig().targets().is32Bits();
  // if (Is32Bits) {
  //   return emitImpl<llvm::object::ELF32LE>(Buf, M);
  // } else {
  //   return emitImpl<llvm::object::ELF64LE>(Buf, M);
  // }
  return {};
}

size_t GNUVerDefFragment::size() const {
  return 0;
}

// template <class ELFT>
// eld::Expected<void> GNUVerDefFragment::emitImpl(uint8_t *Buf, Module &M) {
//   return {};
// }