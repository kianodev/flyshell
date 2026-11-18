# setup.py

from setuptools import Extension, setup
import sys

sources = [
    "c_src/diskops/diskops.c",
    "c_src/diskops/shared/dir_types.c",
]

define_macros = []

if sys.platform == "win32":
    sources.extend(
        [
            "c_src/diskops/win32/cat.c",
            "c_src/diskops/win32/cp.c",
            "c_src/diskops/win32/dir.c",
            "c_src/diskops/win32/mkdir.c",
            "c_src/diskops/win32/mv.c",
            "c_src/diskops/win32/rename.c",
            "c_src/diskops/win32/rm.c",
            "c_src/diskops/win32/rmdir.c",
            "c_src/diskops/win32/touch.c",
        ]
    )
else:
    if sys.platform == "darwin":
        define_macros.append(("_DARWIN_C_SOURCE", "1"))
    sources.extend(
        [
            "c_src/diskops/posix/cat.c",
            "c_src/diskops/posix/cp.c",
            "c_src/diskops/posix/dir.c",
            "c_src/diskops/posix/mkdir.c",
            "c_src/diskops/posix/mv.c",
            "c_src/diskops/posix/rename.c",
            "c_src/diskops/posix/rm.c",
            "c_src/diskops/posix/rmdir.c",
            "c_src/diskops/posix/touch.c",
        ]
    )

native_diskops = Extension(
    name="flyshell.bin._native_diskops",
    sources=sources,
    include_dirs=["c_src/diskops/shared"],
    define_macros=define_macros,
)

setup(
    ext_modules=[native_diskops],
)
