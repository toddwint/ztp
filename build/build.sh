#!/usr/bin/env bash
supported_archs=( "x86_64" "aarch64" )
arch="$(arch)"
arch_match=$(printf '%s\n' "${supported_archs[@]}" | grep $arch )
if [[ -z $arch_match ]]; then
    echo "$arch is not supported. Bye"
    exit 1
fi
docker build -t toddwint/ztp .
