//===- ELFDynObjectFile.h--------------------------------------------------===//
// Part of the eld Project, under the BSD License
// See https://github.com/qualcomm/eld/LICENSE.txt for license information.
// SPDX-License-Identifier: BSD-3-Clause
//===----------------------------------------------------------------------===//
#ifndef ELD_INPUT_ELFDYNOBJECTFILE_H
#define ELD_INPUT_ELFDYNOBJECTFILE_H

#include "eld/Input/ELFFileBase.h"
#include "eld/Input/Input.h"
#include <sys/types.h>

namespace eld {

/** \class ELFDynObjFile
 *  \brief InputFile represents a dynamic shared library.
 */
class ELFDynObjectFile : public ELFFileBase {
public:
  ELFDynObjectFile(Input *I, DiagnosticEngine *DiagEngine);

  /// Casting support.
  static bool classof(const InputFile *I) {
    return (I->getKind() == InputFile::ELFDynObjFileKind);
  }

  std::string getSOName() const { return getInput()->getName(); }

  void setSOName(std::string SOName) { getInput()->setName(SOName); }

  ELFSection *getDynSym() const { return SymbolTable; }

  bool isELFNeeded() override;

  virtual ~ELFDynObjectFile() {}

  void setVerDefSection(ELFSection *S) { VerDefSection = S; }

  ELFSection *getVerDefSection() const { return VerDefSection; }

  void setVerNeedSection(ELFSection *S) { VerNeedSection = S; }

  ELFSection *getVerNeedSection() const { return VerNeedSection; }

  void setVerSymSection(ELFSection *S) { VerSymSection = S; }

  ELFSection *getVerSymSection() const { return VerSymSection; }

  void setVerDefs(std::vector<uint32_t> VDefs) {
    VerDefs = VDefs;
  }

  const std::vector<uint32_t> &getVerDefs() const { return VerDefs; }

  void setVerNeeds(std::vector<uint32_t> VNeeds) {
    VerNeeds = VNeeds;
  }

  const std::vector<uint32_t> &getVerNeeds() const { return VerNeeds; }

  void setVerSyms(std::vector<uint16_t> VSyms) {
    VerSyms = VSyms;
  }

  const std::vector<uint16_t> &getVerSyms() const { return VerSyms; }

  void setDynStrTabSection(ELFSection *S) {
    DynStrTabSection = S;
  }

  llvm::StringRef getDynStringTable() const;

private:
  std::vector<ELFSection *> Sections;
  ELFSection *VerDefSection = nullptr;
  ELFSection *VerNeedSection = nullptr;
  ELFSection *VerSymSection = nullptr;
  ELFSection *DynStrTabSection = nullptr;
  std::vector<uint32_t> VerDefs;
  std::vector<uint32_t> VerNeeds;
  std::vector<uint16_t> VerSyms;
};

} // namespace eld

#endif // ELD_INPUT_ELFDYNOBJECTFILE_H
