ENGINE_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

.PHONY: export
export:
	python3 "$(ENGINE_DIR)scripts/export.py" $(if $(SOURCE),"$(SOURCE)",)
