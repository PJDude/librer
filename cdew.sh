#!/bin/bash

#Custom Data Extraction Wrapper

if [ $# -ne 1 ]; then
  echo "parameter expected !"
  exit 1
fi

file_path="$1"
file_extension="${file_path##*.}"

if [ "$file_extension" = "txt" ]; then
    echo "Text File"
elif [ "$file_extension" = "jpg" ] || [ "$file_extension" = "jpeg" ]; then
    echo "Image"
elif [ "$file_extension" = "sh" ]; then
    echo "Script"
fi
