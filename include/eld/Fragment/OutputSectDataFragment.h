//===- OutputSectDataFragment.h--------------------------------------------===//
// Part of the eld Project, under the BSD License
// See https://github.com/qualcomm/eld/LICENSE.txt for license information.
// SPDX-License-Identifier: BSD-3-Clause
//===----------------------------------------------------------------------===//

#ifndef ELD_FRAGMENT_OUTPUTSECTDATAFRAGMENT_H
#define ELD_FRAGMENT_OUTPUTSECTDATAFRAGMENT_H

#include "eld/Fragment/Fragment.h"
#include "eld/Script/OutputSectData.h"

namespace eld {

/// OutputSectDataFragment is used for output section data linker script
/// keywords: BYTE, SHORT, LONG, ...
class OutputSectDataFragment : public Fragment {
public:
  OutputSectDataFragment(OutputSectData &OutSectData);

  ~OutputSectDataFragment() = default;

  static bool classof(const Fragment *F) {
    return F->getKind() == Fragment::OutputSectDataFragType;
  }

  size_t size() const override;

  virtual eld::Expected<void> emit(MemoryRegion &Mr, Module &M) override;

  bool isFirstFragmentOfInputSection() const override {
    return true;
  }

private:
  OutputSectData &OutSectData;
};
} // namespace eld

#endif
