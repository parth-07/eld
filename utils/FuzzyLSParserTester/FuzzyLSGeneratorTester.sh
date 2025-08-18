#!/usr/bin/env bash

SCRIPTS_DIR=/local/mnt/workspace/partaror/tests/LinkerScripts
ROOT=/local/mnt/workspace/partaror/eld/formal/llvm-project/eld/utils/FuzzyLSParserTester
BASE_LDs=("riscv64-unknown-elf-ld.bfd" ld.lld)
BASE_SFs=(bfd lld)
LD="ld.eld -m elf64lriscv"
SF="eld"
RESULTS_DIR="results"

compute_base_result() {
  f="$1"
  filename="${f##*/}"
  for i in "${!BASE_SFs[@]}"; do
      "${BASE_LDs[$i]}" -o /dev/null /dev/null -T "$f"  1>"$RESULTS_DIR/${filename}.${BASE_SFs[$i]}.log" 2>&1
      ec=$?
      if [ "$ec" -ne 0 ]; then
        should_fail=true
         echo "${BASE_SFs[$i]}:${filename}: FAIL($ec)"
      else
        echo "${BASE_SFs[$i]}:${filename}: PASS"
      fi
  done
}

report_fail_count=0
report_pass_count=0
report_failures=()

check_test() {
  f="$1"
  filename="${f##*/}"
  echo "filename: ${filename}"
  "${ROOT}/FuzzyLSGenerator.py" "$f" "${RESULTS_DIR}/${filename}"
  should_fail=false
  compute_base_result "${RESULTS_DIR}/${filename}"
  if [ "$should_fail" = true ]; then
      echo "${filename}:should_fail: true"
  else
      echo "${filename}:should_fail: false"
  fi
  $LD -o /dev/null /dev/null -T "${RESULTS_DIR}/${filename}"  1>"${RESULTS_DIR}/${filename}.$SF.log" 2>&1
  ec=$?
  failed=false
  if [ "$ec" -ne 0 ]; then
     echo "${SF}:${filename}: FAIL($ec)"
     failed=true
  else
    echo "${SF}:${filename}: PASS"
    failed=false
  fi
  if [ "$failed" = "${should_fail}" ]; then
    echo "${filename}: PASS"
    ((report_pass_count += 1))
  else
    echo "${filename}: FAIL"
    ((report_fail_count += 1))
    report_failures+=("${filename}")
  fi
}

report() {
  echo "----------------------------"
  echo "PASS: ${report_pass_count}"
  echo "FAIL: ${report_fail_count}"
  if [ "${report_fail_count}" -ne 0 ]; then
    printf "\n"
    echo "FAILURES:"
    for f in "${report_failures[@]}"; do
      echo "  - $f"
    done
  fi
  echo "----------------------------"
}

for f in "${SCRIPTS_DIR}"/*; do
  check_test "${f}"
  printf "\n"
done

report