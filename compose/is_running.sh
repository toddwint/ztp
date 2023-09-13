#!/usr/bin/env bash
SCRIPTDIR="$(dirname "$(realpath "$0")")"

# Check that files exist first
FILES=(".env" "compose.yaml")
for FILE in "${FILES[@]}"; do
    if [ ! -f "${SCRIPTDIR}/${FILE}" ]; then
            echo "File not found: ${FILE}"
            echo "Run create_project.sh first."
            exit 1
    fi
done

# Then start by importing environment file
source "${SCRIPTDIR}"/.env

RED='\033[0;31m'
GREEN='\033[0;32m'
NOCOLOR='\033[0m'

COMMAND=$(docker compose ps)
SEARCH=$(echo "${COMMAND}" | grep "${HOSTNAME}")
RC=$?
# test if command ran without errors
if [ ! ${RC} -eq 0 ]; then
    echo "${COMMAND}"
    echo -e "- ${RED}No. It is not running.${NOCOLOR}"
else
    echo "${COMMAND}"
    echo -e "- ${GREEN}Yes. It is running.${NOCOLOR}"
fi
