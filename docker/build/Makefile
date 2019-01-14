TOPDIR = $(realpath ../..)
-include ${TOPDIR}/buildenv.mk

# Do not modified the following
ifdef tag_name
	PKG_VER = $(tag_name)
else
	PKG_VER = $(CONFIG_VERSION_MAJOR).$(CONFIG_VERSION_MINOR).$(CONFIG_BUILD_NO)
endif
PKG_NAME = $(CONFIG_PRODUCT_LOW)-docker_$(PKG_VER)-1

TAG_USER = $(CONFIG_PRODUCT_LOW)
TAG_REPO = $(CONFIG_VENDOR_LOW)
TAG = $(TAG_REPO)/$(TAG_USER):$(PKG_VER)
TAG_LATEST = $(TAG_REPO)/$(TAG_USER):latest
OLD_IMAGES = $(shell docker images | grep "$(TAG_USER)/$(TAG_REPO)" | awk -F" " '{print $$3}')

######################################################################

all: build

build: $(PKG_NAME).tgz

# Create docker package
$(PKG_NAME).tgz: .FORCE

	@if [ ! -f "$(TOPDIR)/buildenv.mk" ]; then \
	    echo ""; \
	    echo "Error in creating build."; \
	    echo "Please run 'make config' under $(TOPDIR) first."; \
	    echo "Abort build creation."; \
	    echo ""; \
	    exit 1; \
	fi

	. ${TOPDIR}/buildenv.mk
	@echo; echo "==============================================="
	@echo "Create $(CONFIG_OEM) docker package: $(CONFIG_PRODUCT_LOW)"
	@echo "==============================================="; echo

	rm -f $(PKG_NAME).tgz
	@for i in $(OLD_IMAGES); do \
		docker rmi $$i; true; \
	done

	docker build --rm=true -t ${TAG} .. 2>&1 | tee build.out
	docker tag ${TAG} ${TAG_LATEST}
	docker save $(TAG_REPO)/$(TAG_USER) | gzip -c > $(PKG_NAME).tgz
	md5sum $(PKG_NAME).tgz > $(PKG_NAME).tgz.md5sum
	docker rmi ${TAG} ${TAG_LATEST}


clobber: clean
	rm -rf *_[0-9]*.[0-9]*.[0-9]*-[0-9]*.tgz *_[0-9]*.[0-9]*.[0-9]*-[0-9]*.tgz.md5sum

clean::
	rm -fv *~ *.tgz *.tgz.md5sum
	rm -f build.out

.FORCE:

