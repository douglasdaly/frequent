#!/bin/bash

# Color constants
if test -t 1; then
    NCOLORS=$(tput colors)
    if test -n "${NCOLORS}" && test ${NCOLORS} -ge 8; then
        BOLD="$(tput bold)"
        NC="$(tput sgr0)"
        RED="$(tput setaf 1)"
        GREEN="$(tput setaf 2)"
        YELLOW="$(tput setaf 3)"
        BLUE="$(tput setaf 4)"
    fi
fi

# Functions

function printo {
    [ -z "$NO_HOOK_OUTPUT" ] && printf "$@"
}

# Variables
ROOT=../..
HOOK="$(basename $0)"
LOG_OUT="${ROOT}"/"${HOOK}".log

# Setup
touch "${LOG_OUT}"

for f in "${ROOT}"/.githooks/"${HOOK}"/*; do
    test -f "$f" || continue

    STEP="$(basename $f)"
    echo "[${HOOK}] (${STEP})" >> "${LOG_OUT}"
    printo "${BOLD}${BLUE}[${HOOK}]${NC} ${BOLD}${YELLOW}%-16s${NC} " "${STEP}"

    TMP_ERR=$(mktemp)
    echo "${f}" >> "${LOG_OUT}"
    OUTPUT=$("${f}" 2> "${TMP_ERR}")
    STATUS="$?"
    SERR=$(cat "${TMP_ERR}")
    rm "${TMP_ERR}"
    echo "${OUTPUT}" >> "${LOG_OUT}"

    if [ ${STATUS} -eq 0 ]
    then
        printo "${BOLD}SUCCESS${NC}\n"
    else
        echo "${SERR}" >> "${LOG_OUT}"
        printo "${BOLD}${RED}FAILED${NC}\n\n"
        printo " ${BLUE}--- OUTPUT ---${NC}\n"
        while read -r l; do
            printo  "    %s\n" "${l}"
        done <<< "$OUTPUT"
        printo "\n"
        printo " ${RED}--- STDERR ---${NC}\n"
        while read -r l; do
            printo "    %s\n" "${l}"
        done <<< "$SERR"
        printo "\n"
        exit 1
    fi

    printf "\n" >> "${LOG_OUT}"
done

rm "${LOG_OUT}"
exit 0

