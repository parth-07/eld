#include "eld/Fragment/GNUVerSymFragment.h"
#include "eld/Core/Module.h"
#include "eld/Target/GNULDBackend.h"

using namespace eld;

GNUVerSymFragment::GNUVerSymFragment(ELFSection *S,
                                     const std::vector<ResolveInfo *> &DynSyms)
    : Fragment(Fragment::Type::GNUVerSym, S), DynamicSymbols(DynSyms) {}

size_t GNUVerSymFragment::size() const {
  return DynamicSymbols.size() * 2;
}

eld::Expected<void> GNUVerSymFragment::emit(MemoryRegion &MR, Module &M) {
  uint8_t *Buf = MR.begin() + getOffset(M.getConfig().getDiagEngine());
  GNULDBackend &Backend = M.getBackend();
  for (const auto *DynSym : DynamicSymbols) {
    auto optVerID = Backend.getSymbolVersionID(DynSym);
    ASSERT(optVerID.has_value(), "All dynamic symbols must have a version ID!");
    uint16_t VerNum = optVerID.value();
    *reinterpret_cast<uint16_t *>(Buf) = VerNum;
    Buf += 2;
  }
  return {};
}
