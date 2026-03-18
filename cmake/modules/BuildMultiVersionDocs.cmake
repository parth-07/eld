# BuildMultiVersionDocs.cmake
#
# Provides CMake targets for building multi-version ELD documentation.
#
# This module creates git worktrees for each configured version, builds
# the eld-docs target for each, and assembles a combined site with a
# landing page and version selector.
#
# Variables (user-configurable):
#   ELD_DOC_VERSIONS - List of "branch:output_name:label" specs
#                      Example: "main:latest:Latest (main);release/22.x:22.x:Release 22.x"
#   ELD_DOC_STABLE   - Which version the "stable" symlink points to (default: 22.x)
#
# Targets created:
#   eld-docs-all-releases  - Builds documentation for all configured versions
#   eld-docs-<name>        - Builds documentation for a single version
#   eld-docs-assemble      - Generates landing page and symlinks (depends on all versions)
#   eld-docs-multiversion  - Convenience target: builds all + assembles
#
# Output:
#   ${CMAKE_BINARY_DIR}/tools/eld/docs/multiversion/
#     ├── index.html
#     ├── versions.json
#     ├── stable -> <ELD_DOC_STABLE>
#     ├── latest/
#     └── 22.x/

function(eld_add_multiversion_doc_targets)
    if(NOT DEFINED ELD_SOURCE_DIR)
        message(FATAL_ERROR "ELD_SOURCE_DIR must be defined before calling eld_add_multiversion_doc_targets")
    endif()

    find_package(Python3 REQUIRED COMPONENTS Interpreter)

    set(ELD_DOC_VERSIONS
        "main:latest:Latest (main)"
        "release/22.x:22.x:Release 22.x"
        CACHE STRING "Semicolon-separated list of 'branch:output_name:label' for multi-version docs")

    set(ELD_DOC_STABLE "22.x"
        CACHE STRING "Version that 'stable' symlink points to")

    set(ELD_MULTIVERSION_SCRIPTS_DIR "${ELD_SOURCE_DIR}/docs/multiversion")
    set(ELD_MULTIVERSION_WORK_DIR "${CMAKE_BINARY_DIR}/tools/eld/docs/multiversion")
    set(ELD_MULTIVERSION_SITE_DIR "${ELD_MULTIVERSION_WORK_DIR}/site")

    # LLVM_SOURCE_DIR points to llvm/ subdirectory; parent is llvm-project root
    get_filename_component(ELD_LLVM_REPO_ROOT "${LLVM_SOURCE_DIR}/.." ABSOLUTE)
    if(NOT DEFINED LLVM_SOURCE_DIR OR NOT EXISTS "${ELD_LLVM_REPO_ROOT}/llvm/CMakeLists.txt")
        message(WARNING "LLVM_SOURCE_DIR not set or invalid")
        message(WARNING "Multi-version docs target will not be available")
        return()
    endif()

    set(version_targets "")
    set(versions_json "[")
    set(first_version TRUE)

    foreach(version_spec IN LISTS ELD_DOC_VERSIONS)
        # Parse "branch:output_name:label"
        string(REPLACE ":" ";" parts "${version_spec}")
        list(LENGTH parts num_parts)

        if(num_parts LESS 2)
            message(WARNING "Invalid version spec (need at least branch:output_name): ${version_spec}")
            continue()
        endif()

        list(GET parts 0 branch)
        list(GET parts 1 output_name)
        if(num_parts GREATER_EQUAL 3)
            list(GET parts 2 label)
        else()
            set(label "${output_name}")
        endif()

        # Determine version attributes for JSON
        set(is_stable FALSE)
        set(is_dev FALSE)
        if(output_name STREQUAL "${ELD_DOC_STABLE}")
            set(is_stable TRUE)
        endif()
        if(output_name STREQUAL "latest")
            set(is_dev TRUE)
        endif()

        # Build JSON entry for this version
        if(NOT first_version)
            string(APPEND versions_json ",")
        endif()
        set(first_version FALSE)

        string(APPEND versions_json "{\"path\":\"${output_name}\",\"label\":\"${label}\"")
        if(is_stable)
            string(APPEND versions_json ",\"stable\":true")
        endif()
        if(is_dev)
            string(APPEND versions_json ",\"dev\":true")
        endif()
        string(APPEND versions_json "}")

        # Create target for this version
        set(target_name "eld-docs-${output_name}")

        add_custom_target(${target_name}
            COMMAND ${Python3_EXECUTABLE}
                "${ELD_MULTIVERSION_SCRIPTS_DIR}/build_docs.py"
                --branch "${branch}"
                --output-name "${output_name}"
                --eld-repo "${ELD_SOURCE_DIR}"
                --llvm-repo "${ELD_LLVM_REPO_ROOT}"
                --work-dir "${ELD_MULTIVERSION_WORK_DIR}"
                --output-dir "${ELD_MULTIVERSION_SITE_DIR}"
                --version-label "${label}"
            WORKING_DIRECTORY "${CMAKE_BINARY_DIR}"
            COMMENT "Building ELD docs: ${branch} -> ${output_name}"
            USES_TERMINAL
            VERBATIM
        )

        list(APPEND version_targets ${target_name})
    endforeach()

    string(APPEND versions_json "]")

    # Main target that builds all versions
    add_custom_target(eld-docs-all-releases
        DEPENDS ${version_targets}
        COMMENT "Building all ELD documentation versions"
    )

    # Assembly target that generates landing page and symlinks
    add_custom_target(eld-docs-assemble
        DEPENDS eld-docs-all-releases
        COMMAND ${Python3_EXECUTABLE}
            "${ELD_MULTIVERSION_SCRIPTS_DIR}/assemble_site.py"
            --site-dir "${ELD_MULTIVERSION_SITE_DIR}"
            --versions "${versions_json}"
        WORKING_DIRECTORY "${CMAKE_BINARY_DIR}"
        COMMENT "Assembling multi-version documentation site"
        USES_TERMINAL
        VERBATIM
    )

    # Convenience target that does everything
    add_custom_target(eld-docs-multiversion
        DEPENDS eld-docs-assemble
        COMMENT "Multi-version documentation complete: ${ELD_MULTIVERSION_SITE_DIR}"
    )

    message(STATUS "Multi-version docs target: eld-docs-all-releases")
    message(STATUS "  Versions: ${ELD_DOC_VERSIONS}")
    message(STATUS "  Stable: ${ELD_DOC_STABLE}")
    message(STATUS "  Output: ${ELD_MULTIVERSION_SITE_DIR}")

endfunction()
