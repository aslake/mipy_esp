# Script for compiling og minified nanogram CSS in chip code source.
# Tailoring of Nanogram CSS framework from .sass files in /css/src/nanogram
#
# Author: Aslak Einbu, Jan 2020

sass ../src/nanogram/nanogram.sass nanogram.css
echo "New nanogram.css compiled from sass files!"

cat nanogram.css| tr -d " \t\n\r" > nanogram.min.css
echo "Nanogram successfully minified!"

cp nanogram.min.css ../../src/nanogram.min.css
echo "New nanogram.min.css written to /src !"
