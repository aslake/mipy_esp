SHELL := /bin/bash

# MiPy-ESP MicroPython Microcontroller Basic Framework Makefile.
#
# .py conversion to .mpy needs installation of the mpy-cross compiler:
# https://github.com/micropython/micropython/tree/master/mpy-cross
#
# ESP commands depends on the ESPTOOL software:
# https://github.com/espressif/esptool)


build:	## Compile src .py files and move to /build
	@echo ----------------------------------------------------
	@echo - Prepare for chip upload  -
	@echo ----------------------------------------------------
	@mkdir -p build                                  
	@echo Compiles .py files to .mpy:
	@for f in src/*.py; do mpy-cross $$f; echo "    cp $$f"; done;    
	@rm src/main.mpy
	@rm src/boot.mpy
	@rm src/config.mpy
	@mv src/*.mpy build
	@echo Moved all compiled .mpy files to build.
	@cp src/main.py build
	@cp src/config.py build
	@cp src/boot.py build
	@echo Copied main.py, config.py and boot.py to build.
	@echo Copy html, ccs, js and json files to build:
	@for f in src/*.html; do cp $$f build; echo "  cp" $$f; done;
	@for f in src/*.css; do cp $$f build; echo "  cp" $$f; done;
	@for f in src/*.js; do cp $$f build; echo "  cp" $$f; done;
	@for f in src/*.json; do cp $$f build; echo "  cp" $$f; done;
	@echo ----------------------------------------------------
	@echo Files in build ready for upload to chip:
	@tree -sh build


erase_chip: ## Erase ESP flash memory
	@echo ------------------------------------
	@echo - Erases ESP flash memory -
	@echo ------------------------------------
	@esptool.py --port /dev/ttyUSB0 erase_flash
	@echo Microcontroller flash erased.


flash_chip: ## Uploads Micropython to ESP 
	@echo ------------------------------------
	@echo - Upload MicroPython to ESP chip -
	@echo ------------------------------------
	@esptool.py --port /dev/ttyUSB0 --baud 460800 write_flash --flash_size=detect 0 ~/Downloads/esp8266-20191220-v1.12.bin
	@echo MicroPython installed on ESP microcontroller!


clean: ## Remove build folder
	@echo ----------------------------------------------
	@echo - Removes build/ folder and its content  -
	@echo ----------------------------------------------
	@rm -r build
	@echo Build folder erased.


.PHONY: build erase_flash cleann
