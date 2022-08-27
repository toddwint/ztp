#!/usr/bin/env bash
source "$(dirname "$(realpath $0)")"/config.txt
folder="$(eval "echo $(awk '/^\t*\s*-v/ {print $2}' create_container.sh | awk -F: '{print $1}')")"
echo -e "Removing \`$folder\`"
rm -rf "$folder"
