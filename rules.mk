LOCAL_DIR := $(GET_LOCAL_DIR)
MODULE := $(LOCAL_DIR)
MODULE_TYPE := userapp
MODULE_SRCS += \
    $(LOCAL_DIR)/driver.c \
    $(LOCAL_DIR)/parse.c \
    $(LOCAL_DIR)/sysc.c \
    $(LOCAL_DIR)/aflCall.c \
    $(LOCAL_DIR)/argfd.c
MODULE_NAME := fuzz
MODULE_LIBS := system/ulib/magenta system/ulib/mxio system/ulib/c system/ulib/launchpad
USER_MANIFEST_LINES += src/ex1=$(LOCAL_DIR)/inputs/ex1
include make/module.mk
