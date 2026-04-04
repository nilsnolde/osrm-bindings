DATA_NAME:=monaco
PROFILE_ROOT:=profiles
PYOSRM_CMD:=python -m osrm
OSRM_EXTRACT:=$(PYOSRM_CMD) extract
OSRM_CONTRACT:=$(PYOSRM_CMD) contract
OSRM_PARTITION:=$(PYOSRM_CMD) partition
OSRM_CUSTOMIZE:=$(PYOSRM_CMD) customize
PROFILE:=$(PROFILE_ROOT)/car.lua

all: data

data: ch/$(DATA_NAME).osrm.hsgr mld/$(DATA_NAME).osrm.partition

clean:
	-rm -r $(DATA_NAME).*
	-rm -r ch mld

ch/$(DATA_NAME).osrm: $(DATA_NAME).osrm
	mkdir -p ch
	cp $(DATA_NAME).osrm.* ch/

mld/$(DATA_NAME).osrm: $(DATA_NAME).osrm
	mkdir -p mld
	cp $(DATA_NAME).osrm.* mld/

$(DATA_NAME).osrm: $(DATA_NAME).osm.pbf $(DATA_NAME).poly $(PROFILE)
	@echo "Running osrm-extract..."
	$(OSRM_EXTRACT) $< -p $(PROFILE)

ch/$(DATA_NAME).osrm.hsgr: ch/$(DATA_NAME).osrm $(PROFILE)
	@echo "Running osrm-contract..."
	$(OSRM_CONTRACT) $<

mld/$(DATA_NAME).osrm.partition: mld/$(DATA_NAME).osrm $(PROFILE)
	@echo "Running osrm-partition..."
	$(OSRM_PARTITION) $<
	$(OSRM_CUSTOMIZE) $<

.PHONY: clean data
