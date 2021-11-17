#!/bin/bash
# Compile MicroPython source to smaller .mpy files
# and send the files to a Nucleo, ESP32, or whatever


send_mpies ()
{
	if [ -d "/media/jr/PYBFLASH" ]; then
		for afile in $1 ; do
		    cp -p $afile /media/jr/PYBFLASH
		done
	else
    	echo "No PYBFLASH mounted; not copying."
	fi

	if [ -e "/dev/ttyUSB0" ]; then
    	for a_file in $1 ; do
        	echo Copying: $a_file
	        ampy -p /dev/ttyUSB0 -b 115200 put $a_file
    	done	
	fi
}


if "$1" == "" ; then
	for filename in `ls upd_*.py` main.py micropydash.py ; do
    	echo Compiling: $filename
    	python3 -m mpy_cross $filename;
	done
else
	files=$1
fi


for filename in $files ; do
   	echo Compiling: $filename
   	python3 -m mpy_cross $filename;
done


send_mpies $files



