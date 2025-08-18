#!/usr/bin/env bash

ROOT="$(realpath "$(dirname "$0")")"
ELD_SOURCE_DIR="$(realpath "${ROOT}/../..")"
SCRIPTS_DIR="${ELD_SOURCE_DIR}/test/Common"
LD="ld.eld -m elf64lriscv"
SF="eld"

RESULTS_DIR="/local/mnt/workspace/partaror/eld/formal/obj/results"

report_pass_count=0
report_fail_count=0
report_failures=()

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

log() {
  2>&1 echo "$@"
}

should_validate_parsing() {
  (
    # cd "$(dirname "$1")"
    if LSParserVerifier "$1" 1>/dev/null 2>&1; then
      exit 0
    fi
    exit 1
  )
  ec="$?"
  # echo "ec: $ec"
  if [[ $ec -ne 0 ]]; then
    log "Skipping $1"
    return 1
  fi
  return 0
}

get_relative_path_to_scripts_dir() {
  relative_path="$(realpath -s --relative-to="${SCRIPTS_DIR}" "$1")"
  echo "${relative_path}"
}

get_output_filename() {
  relative_path="$(get_relative_path_to_scripts_dir "$1")"
  output_file="${RESULTS_DIR}/${relative_path}.LSG.t"
  mkdir -p "$(dirname "${output_file}")"
  echo "${output_file}"
}

run_linker_script_generator() {
  (
    input_f="$1"
    output_f="$2"
    cd "$(dirname "${input_f}")"
    ${LD} -o /dev/null /dev/null -T ${input_f} \
      --plugin-config "${ROOT}/LinkerScriptGeneratorPluginConfig.yaml" \
      >"${output_f}" 2>/dev/null
  )
}

validate_parsing() {
  f="$1"
  relative_f="$(get_relative_path_to_scripts_dir "$f")"
  log "Validating ${relative_f}"
  output_file="$(get_output_filename "$f")"
  run_linker_script_generator "$f" "${output_file}"
  ec=$?
  if [ $ec -ne 0 ]; then
      echo "  - ${relative_f}: Linker error"
    return
  fi
  python3 ${ROOT}/CompareLinkerScripts.py "${f}" "${output_file}"
  ec=$?
  if [ $ec -eq 0 ]; then
    echo -e "  - ${relative_f}:${GREEN} PASS${NC}"
    ((report_pass_count+=1))
  else
    echo -e "  - ${relative_f}:${RED} FAIL${NC}"
    ((report_fail_count+=1))
    report_failures+=("${relative_f}")
  fi
}

report() {
  echo "----------------"
  echo "Report"
  echo "----------------"
  echo "Pass count: ${report_pass_count}"
  echo "Fail count: ${report_fail_count}"
  if [ "${report_fail_count}" -ne 0 ]; then
    printf "\n"
    echo "Failures:"
    for f in "${report_failures[@]}"; do
      echo "${f}"
    done
  fi
}

readarray -d '' scripts < <(find "${SCRIPTS_DIR}" -type f -iname '*.t' -print0)

count=0
for script in "${scripts[@]}"; do
  if should_validate_parsing "${script}"; then
    validate_parsing "$script"
    ((count+=1))
    printf "\n"
  fi
  if [[ count -gt 10 ]]; then
    break
  fi
done

report