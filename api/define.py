# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright (c) 2013-2018 ProphetStor Data Services, Inc.
# All Rights Reserved.
#
"""
Defines for ProphetStor Alameter
"""
import os

VENDOR_SHORT = "ProphetStor"
PRODUCT_NAME = "Alameter API"
PRODUCT_NAME_LOWER = "alameter"

if os.name == 'nt':
    # Windows platform
    from win32com.shell import shell, shellcon
    HOME_DEFAULT = "%s\\%s" % (shell.SHGetFolderPath(
        0, shellcon.CSIDL_PROGRAM_FILES, None, 0), PRODUCT_NAME)

else:
    # Linux platform
    HOME_DEFAULT = "/opt/%s/%s" % (VENDOR_SHORT.lower(),
                                   PRODUCT_NAME_LOWER.lower())


if __name__ == "__main__":
    print("PRODUCT_NAME = %s" % PRODUCT_NAME)
    print("HOME_DEFAULT = %s" % HOME_DEFAULT)
    print("PRODUCT_NAME_LOWER = %s" % PRODUCT_NAME_LOWER)
