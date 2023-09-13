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

# Backup log files
echo "Copying transfer report to host."
docker compose exec -it ztp bash -c '/opt/"${APPNAME}"/debug/save_transfer_report.sh'

# Restart the docker project
echo "Restarting the container: ${HOSTNAME}"
docker compose restart
