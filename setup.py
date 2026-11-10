# setup.py

from setuptools import Extension, setup
import sys

sources = [
    "c_src/diskops/diskops.c",
]

if sys.platform == "win32":
    sources.append("c_src/diskops/win32/cat.c")
    sources.append("c_src/diskops/win32/touch.c")
else:
    sources.append("c_src/diskops/posix/cat.c")
    sources.append("c_src/diskops/posix/touch.c")

native_diskops = Extension(
    name="flyshell.bin._native_diskops",
    sources=sources,
    include_dirs=["c_src/diskops/shared"],
)

setup(
    ext_modules=[native_diskops],
)
