#!/bin/bash
set -e -o pipefail

ARGS=('--title' \
"Show me the example of a great og image"  \
'--subtitle'  \
"Of zoiets" \
"--author" \
"Mark van Holsteijn")

for i in $(ls *.png *.jpg  | grep -v -e generated- -e og-) ; do
	python -m binx_og_image_generator "${ARGS[@]}" --output generated-$i $i 
	python -m binx_og_image_generator --email mark.vanholsteijn@xebia.com "${ARGS[@]}" --output generated-with-picture-$i $i 
done
