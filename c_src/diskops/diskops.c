// c_src/diskops/diskops.c

#define PY_SSIZE_T_CLEAN
#include <Python.h>


static PyObject* method_ping(PyObject* self, PyObject* args) {
    return PyLong_FromLong(42);
}


static PyMethodDef NativeDiskMethods[] = {
    {"ping", method_ping, METH_NOARGS, "Test connectivity to C engine."},
    {NULL, NULL, 0, NULL}
};


static struct PyModuleDef nativediskmodule = {
    PyModuleDef_HEAD_INIT,
    "_native_diskops",
    "Native C engine backend for Flyshell",
    -1,
    NativeDiskMethods
};


PyMODINIT_FUNC PyInit__native_diskops(void) {
    return PyModule_Create(&nativediskmodule);
}
