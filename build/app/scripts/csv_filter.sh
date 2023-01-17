#!/usr/bin/env bash

# Usuage `csv_filter.sh <csv_filename>`

csvfile="ztp.csv"
if [ $# -gt 0 ]
    then csvfile="$1"
fi
name="${csvfile%%.*}"
ext="${csvfile##*.}"

echo Input file: "$csvfile"
echo Input filename: "$name"
echo Input file ext: "$ext"

# Make backup of original file
echo Copying "$csvfile" to "$name"-all."$ext"
cp "$csvfile" "$name"-all."$ext"

# By vender
echo Generating "$name"-juniper."$ext"
echo Generating "$name"-aruba."$ext"
sed -E '1p; /^[^,]*(345|1500|7024)[^,]*,/!d' "$csvfile" > "$name"-juniper."$ext"
sed -E '1p; /^[^,]*2930[^,]*,/!d' "$csvfile" > "$name"-aruba."$ext"

# By model
echo Generating "$name"-srx1500."$ext"
echo Generating "$name"-srx345."$ext"
echo Generating "$name"-2930f."$ext"
echo Generating "$name"-acx7024."$ext"
sed -E '1p; /^[^,]*1500[^,]*,/!d' "$csvfile" > "$name"-srx1500."$ext"
sed -E '1p; /^[^,]*345[^,]*,/!d' "$csvfile" > "$name"-srx345."$ext"
sed -E '1p; /^[^,]*2930[^,]*,/!d' "$csvfile" > "$name"-2930f."$ext"
sed -E '1p; /^[^,]*7024[^,]*,/!d' "$csvfile" > "$name"-acx7024."$ext"

