// c_src/diskops/diskops.c

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include "shared/native_errors.h"

Result cat(const char* path, char** out_buf, size_t* out_size);

Result touch(const char* path);

static PyObject* method_ping(PyObject* self, PyObject* args) {
    return PyLong_FromLong(42);
}

static PyObject* method_cat(PyObject* self, PyObject* args) {
    const char* path;
    if (!PyArg_ParseTuple(args, "s", &path)) {
        return NULL;
    }

    char* buf = NULL;
    size_t size = 0;
    Result res = cat(path, &buf, &size);

    if (res != SUCCESS) {
        return Py_BuildValue("(is)", (int)res, "");
    }

    PyObject* content = PyUnicode_FromStringAndSize(buf, size);
    free(buf);

    if (!content) {
        PyErr_Clear();
        return Py_BuildValue("(is)", (int)ERR_DECODE, "");
    }

    PyObject* ret = Py_BuildValue("(iN)", (int)SUCCESS, content);
    return ret;
}

static PyObject* method_touch(PyObject* self, PyObject* args) {
    const char* path;
    if (!PyArg_ParseTuple(args, "s", &path)) {
        return NULL;
    }

    Result res = touch(path);
    return Py_BuildValue("(is)", (int)res, "");
}

static PyMethodDef DiskopsMethods[] = {
    {"ping", method_ping, METH_NOARGS, "Health check ping."},
    {"cat",  method_cat,  METH_VARARGS, "Read file content natively."},
    {"touch", method_touch, METH_VARARGS, "Touch or create file natively."},
    {NULL, NULL, 0, NULL},
};

static struct PyModuleDef diskopsmodule = {
    PyModuleDef_HEAD_INIT,
    "_native_diskops",
    "Flyshell native disk operations.",
    -1,
    DiskopsMethods
};

PyMODINIT_FUNC PyInit__native_diskops(void) {
    return PyModule_Create(&diskopsmodule);
}
