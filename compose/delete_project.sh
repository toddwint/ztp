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

# Stop the docker project
echo "Stopping the container: ${HOSTNAME}"
docker compose down

# Remove the docker networking interface
echo '- - - - -'
echo "Removing docker network: ${INTERFACE}-macvlan"
docker network rm "${INTERFACE}-macvlan"

# test if previous command ran without errors
RC=$?
if [ ! ${RC} -eq 0 ]; then exit; fi

# Remove the management networking interface
echo "Removing management network: ${INTERFACE}-macvlan"
sudo ip link del "${INTERFACE}-macvlan"

# Remove the docker compose.yaml customized files
echo '- - - - -'
echo -e "Removing docker compose file: compose.yaml"
rm -rf "${SCRIPTDIR}"/compose.yaml

# Remove the webadmin.html customized files
echo -e "Removing webadmin file: webadmin.html"
rm -rf "${SCRIPTDIR}"/webadmin.html

# Remove the .env file
echo -e "Removing environment file: .env"
rm -rf "${SCRIPTDIR}"/.env
