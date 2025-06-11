# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [V2] - 2025-06-11

### Added
- Add commit changelog step
- Add tag arg
- Add --tag to git cliff
- Add cliff config
- Add support for asciidoc documentation. by @quic-shaksuma in [#122](https://github.com/qualcomm/eld/pull/122)
- Add a warning for empty segments by @parth-07 in [#117](https://github.com/qualcomm/eld/pull/117)
- Add warn diagnostics for zero-sized memory regions by @parth-07 in [#115](https://github.com/qualcomm/eld/pull/115)

### Changed
- Trying changelog generator
- Make dynamic string table simpler to use by @parth-07 in [#95](https://github.com/qualcomm/eld/pull/95)
- [RISCV] Remove -riscv-asm-relax-branches Flag by @lenary in [#121](https://github.com/qualcomm/eld/pull/121)

## New Contributors
* @parth-07 made their first contribution in [#95](https://github.com/qualcomm/eld/pull/95)
* @lenary made their first contribution in [#121](https://github.com/qualcomm/eld/pull/121)
* @quic-shaksuma made their first contribution in [#122](https://github.com/qualcomm/eld/pull/122)
## [V1] - 2025-05-27

### Added
- Add `ELD_REGISTER_PLUGIN` macro by @parth-07 in [#109](https://github.com/qualcomm/eld/pull/109)
- Support 'archive: member' file-pattern in input section description by @parth-07 in [#68](https://github.com/qualcomm/eld/pull/68)
- Support omagic by @quic-seaswara in [#99](https://github.com/qualcomm/eld/pull/99)
- Support building eld when BUILD_SHARED_LIBS=On by @quic-seaswara in [#86](https://github.com/qualcomm/eld/pull/86)
- Add emulation option support for hexagon, arm and aarch64 by @parth-07 in [#55](https://github.com/qualcomm/eld/pull/55)
- Add primitive support of emulation options with ld.eld by @parth-07 in [#23](https://github.com/qualcomm/eld/pull/23)
- Add delimiter to "cannot read" diagnostic by @androm3da in [#19](https://github.com/qualcomm/eld/pull/19)
- Add "cstring" include for test case by @androm3da in [#12](https://github.com/qualcomm/eld/pull/12)
- Add exidx_start and exidx_end symbols with PROVIDE_HIDDEN semantics by @parth-07 in [#25](https://github.com/qualcomm/eld/pull/25)
- Add FAQ on linker script changes required for TLS functionality by @parth-07 in [#30](https://github.com/qualcomm/eld/pull/30)
- Add permissions for contents and statuses in CI by @navaneethshan in [#18](https://github.com/qualcomm/eld/pull/18)
- Add missing unordered_map include by @quic-seaswara in [#14](https://github.com/qualcomm/eld/pull/14)
- Add CI workflow with GitHub Actions by @navaneethshan in [#7](https://github.com/qualcomm/eld/pull/7)
- Add repolinter workflow by @mynameistechno in [#2](https://github.com/qualcomm/eld/pull/2)

### Changed
- Local symbols that need GOT slot require dynamic relocation by @quic-seaswara in [#102](https://github.com/qualcomm/eld/pull/102)
- [LinkerScript] Parse symbol assignment inside PROVIDE in LexState::Expr by @parth-07 in [#83](https://github.com/qualcomm/eld/pull/83)
- Rename all `LayoutPrinter` class to `LayoutInfo` by @MSMazaya in [#81](https://github.com/qualcomm/eld/pull/81)
- Fix dot counter handling for non-alloc sections by @parth-07 in [#92](https://github.com/qualcomm/eld/pull/92)
- Fix generation of duplicate DT_NEEDED entries by @parth-07 in [#48](https://github.com/qualcomm/eld/pull/48)
- [risc-v] Add --no-relax-zero option by @quic-akaryaki in [#49](https://github.com/qualcomm/eld/pull/49)
- [risc-v] Zero-page (offset from 0) relaxation by @quic-akaryaki
- [RISCV][NFC] Move Relaxation Relocations by @lenary in [#93](https://github.com/qualcomm/eld/pull/93)
- Assignments/defsym needs to be processed in link order by @quic-seaswara in [#61](https://github.com/qualcomm/eld/pull/61)
- [RISCV] Fix QC Relocation Tests by @lenary in [#90](https://github.com/qualcomm/eld/pull/90)
- [PluginAPI] findConfigFile() should return errors by @quic-areg in [#89](https://github.com/qualcomm/eld/pull/89)
- [LSParser] Ignore non-ascii unicode characters by @parth-07 in [#66](https://github.com/qualcomm/eld/pull/66)
- Unconditionally create internal RISCV AttributeFragment by @parth-07 in [#65](https://github.com/qualcomm/eld/pull/65)
- Explicitly disable copying/moving GeneralOptions and export GnuLdDriver by @parth-07 in [#63](https://github.com/qualcomm/eld/pull/63)
- Rename ColorMsg.cmake to ELDColorMsg.cmake by @parth-07 in [#57](https://github.com/qualcomm/eld/pull/57)
- [LinkerScript] Add support for ALIGN_WITH_INPUT by @quic-seaswara in [#53](https://github.com/qualcomm/eld/pull/53)
- [RISC-V] Disable default attribute mix warnings by @apazos in [#39](https://github.com/qualcomm/eld/pull/39)
- [riscv] More cases of using PLT address by @quic-akaryaki in [#41](https://github.com/qualcomm/eld/pull/41)
- Include <windows.h> for case-sensitive targets by @androm3da in [#46](https://github.com/qualcomm/eld/pull/46)
- Change __FUNCSIG__ guard to _MSC_VER by @androm3da in [#45](https://github.com/qualcomm/eld/pull/45)
- Cmake - configure eld to create symlinks by @quic-seaswara in [#44](https://github.com/qualcomm/eld/pull/44)
- Eld version output should be emitted to stdout by @quic-seaswara in [#43](https://github.com/qualcomm/eld/pull/43)
- Update README by @quic-seaswara in [#40](https://github.com/qualcomm/eld/pull/40)
- [Xqci] Add R_RISCV_QC_* Relocation Tests by @lenary in [#16](https://github.com/qualcomm/eld/pull/16)
- Change sort-section to permit space-delim by @androm3da in [#17](https://github.com/qualcomm/eld/pull/17)
- DiagnosticEngine: sort the list of diagnostics includes by @lsahn-gh in [#20](https://github.com/qualcomm/eld/pull/20)
- [Target] Fix typos discovered by codespell (NFC) by @svs-quic in [#37](https://github.com/qualcomm/eld/pull/37)
- Temporary update for ci workflow by @quic-seaswara in [#36](https://github.com/qualcomm/eld/pull/36)
- [NFC] remove first few blank lines in the test by @quic-seaswara in [#35](https://github.com/qualcomm/eld/pull/35)
- [NFC] Refactor RISC-V relocation functions by @quic-akaryaki in [#34](https://github.com/qualcomm/eld/pull/34)
- Free plugin resources before unloading the plugin by @parth-07 in [#33](https://github.com/qualcomm/eld/pull/33)
- [arm] Support --target2=abs/rel/got-rel by @quic-akaryaki in [#31](https://github.com/qualcomm/eld/pull/31)
- Fix typo by @berkus in [#26](https://github.com/qualcomm/eld/pull/26)
- [lld-test] Extend range of AARCH64_ABS16/32 by @quic-akaryaki in [#28](https://github.com/qualcomm/eld/pull/28)
- Allow --patch-enable and local symbol stripping by @quic-akaryaki in [#27](https://github.com/qualcomm/eld/pull/27)
- Fix cleanup step to always run by @navaneethshan in [#10](https://github.com/qualcomm/eld/pull/10)
- Clang-tidy :- by @quic-seaswara in [#11](https://github.com/qualcomm/eld/pull/11)
- [RISCV] Update linker tests for the C ext implication change by @quic-seaswara in [#8](https://github.com/qualcomm/eld/pull/8)
- Minor changes to contributing to eld by @quic-seaswara in [#6](https://github.com/qualcomm/eld/pull/6)
- Replace quic coc email with qualcomm by @mynameistechno in [#5](https://github.com/qualcomm/eld/pull/5)
- Minor changes to README by @quic-seaswara in [#4](https://github.com/qualcomm/eld/pull/4)
- Minor changes to documentation by @anshu-dasgupta in [#3](https://github.com/qualcomm/eld/pull/3)
- Open source eld linker by @quic-seaswara
- Initial commit by @quic-seaswara

### Fixed
- Fix dllexport by @quic-seaswara in [#97](https://github.com/qualcomm/eld/pull/97)
- Fix name of RISC-V extension by @quic-seaswara in [#13](https://github.com/qualcomm/eld/pull/13)

### Removed
- Remove redundant TextLayoutPrinter::destroy function by @parth-07 in [#78](https://github.com/qualcomm/eld/pull/78)

## New Contributors
* @quic-seaswara made their first contribution in [#102](https://github.com/qualcomm/eld/pull/102)
* @MSMazaya made their first contribution in [#81](https://github.com/qualcomm/eld/pull/81)
* @quic-akaryaki made their first contribution in [#49](https://github.com/qualcomm/eld/pull/49)
* @lenary made their first contribution in [#93](https://github.com/qualcomm/eld/pull/93)
* @quic-areg made their first contribution in [#89](https://github.com/qualcomm/eld/pull/89)
* @apazos made their first contribution in [#39](https://github.com/qualcomm/eld/pull/39)
* @androm3da made their first contribution in [#46](https://github.com/qualcomm/eld/pull/46)
* @lsahn-gh made their first contribution in [#20](https://github.com/qualcomm/eld/pull/20)
* @svs-quic made their first contribution in [#37](https://github.com/qualcomm/eld/pull/37)
* @berkus made their first contribution in [#26](https://github.com/qualcomm/eld/pull/26)
* @navaneethshan made their first contribution in [#18](https://github.com/qualcomm/eld/pull/18)
* @mynameistechno made their first contribution in [#5](https://github.com/qualcomm/eld/pull/5)
* @anshu-dasgupta made their first contribution in [#3](https://github.com/qualcomm/eld/pull/3)
[V2]: https://github.com/qualcomm/eld/compare/V1..V2

<!-- generated by git-cliff -->
