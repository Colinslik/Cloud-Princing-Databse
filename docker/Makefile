TOPDIR = $(realpath ..)
-include ${TOPDIR}/buildenv.mk

######################################################################

all: build

gui: .FORCE
	mkdir build/api build/api/db build/api/res build/api/etc build/api/src build/api/common
	cp ../api/alameter_api.wsgi build/api
	cp ../api/*.py build/api
	cp ../api/res/*.py build/api/res
	cp ../api/db/*.py build/api/db
	cp ../api/common/*.py build/api/common
	cp ../service/src/*.py build/api/src
	cp ../service/etc/alameter.conf build/api/etc/alameter.conf
	cp ../service/etc/alameter.conf.user.template build/api/etc/alameter.conf.user

build: .FORCE gui
	@make -C build $@

clean clobber:
	rm -rf build/api
	@make -C build $@

.FORCE: clobber

