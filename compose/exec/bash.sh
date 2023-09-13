#!/usr/bin/env bash
SCRIPTDIR="$(dirname "$(dirname "$(realpath "$0")")")"

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
set -x

docker compose exec -it "${APPNAME}" bash
