#ifndef ELD_FRAGMENT_GNUVERDEFFRAGMENT_H
#define ELD_FRAGMENT_GNUVERDEFFRAGMENT_H

#include "eld/Fragment/Fragment.h"
#include <vector>
#include <cstdint>

namespace eld {

class GNUVerDefFragment : public Fragment {
public:
  GNUVerDefFragment(ELFSection *S);

  static bool classof(const Fragment *F) {
    return F->getKind() == Fragment::Type::GNUVerDef;
  }

  eld::Expected<void> emit(MemoryRegion &Mr, Module &M) override;

  size_t size() const override;

private:
};

} // namespace eld

#endif // ELD_FRAGMENT_GNUVERDEFFRAGMENT_H