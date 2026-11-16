// c_src/diskops/diskops.c

#define PY_SSIZE_T_CLEAN
#include "shared/dir_types.h"
#include "shared/native_errors.h"
#include <Python.h>

Result cat(const char *path, char **out_buf, size_t *out_size);

Result touch(const char *path);

Result list_dir(const char *path, DirList *out_list);

Result make_dir(const char *path, bool parents);

Result rename_item(const char *src, const char *dst);

Result remove_dir(const char *path, bool force);

Result remove_item(const char *path, bool recursive);

static PyObject *method_ping(PyObject *self, PyObject *args) {
    return PyLong_FromLong(42);
}

static PyObject *method_cat(PyObject *self, PyObject *args) {
    const char *path;
    if (!PyArg_ParseTuple(args, "s", &path)) {
        return NULL;
    }

    char *buf = NULL;
    size_t size = 0;
    Result res = cat(path, &buf, &size);

    if (res != SUCCESS) {
        return Py_BuildValue("(is)", (int)res, "");
    }

    PyObject *content = PyUnicode_FromStringAndSize(buf, (Py_ssize_t)size);
    free(buf);

    if (!content) {
        PyErr_Clear();
        return Py_BuildValue("(is)", (int)ERR_DECODE, "");
    }

    PyObject *ret = Py_BuildValue("(iN)", (int)SUCCESS, content);
    return ret;
}

static PyObject *method_touch(PyObject *self, PyObject *args) {
    const char *path;
    if (!PyArg_ParseTuple(args, "s", &path)) {
        return NULL;
    }

    Result res = touch(path);
    return Py_BuildValue("(is)", (int)res, "");
}

static PyObject *method_dir(PyObject *self, PyObject *args) {
    const char *path;
    if (!PyArg_ParseTuple(args, "s", &path)) {
        return NULL;
    }

    DirList dir_list;
    Result res = list_dir(path, &dir_list);
    if (res != SUCCESS) {
        return Py_BuildValue("(i[])", (int)res);
    }

    PyObject *py_list = PyList_New((Py_ssize_t)dir_list.count);
    if (!py_list) {
        PyErr_Clear();
        free_dir_list(&dir_list);
        return Py_BuildValue("(i[])", (int)ERR_IO);
    }

    for (size_t i = 0; i < dir_list.count; ++i) {
        PyObject *item = Py_BuildValue("(sO)", dir_list.entries[i].name,
                                       dir_list.entries[i].is_dir ? Py_True : Py_False);
        if (!item) {
            PyErr_Clear();
            Py_DECREF(py_list);
            free_dir_list(&dir_list);
            return Py_BuildValue("(i[])", (int)ERR_DECODE);
        }
        PyList_SET_ITEM(py_list, (Py_ssize_t)i, item);
    }

    free_dir_list(&dir_list);
    return Py_BuildValue("(iN)", (int)SUCCESS, py_list);
}

static PyObject *method_mkdir(PyObject *self, PyObject *args) {
    const char *path;
    int parents = 0;
    if (!PyArg_ParseTuple(args, "s|p", &path, &parents)) {
        return NULL;
    }

    Result res = make_dir(path, parents != 0);
    return Py_BuildValue("(is)", (int)res, "");
}

static PyObject *method_rename(PyObject *self, PyObject *args) {
    const char *src;
    const char *dst;
    if (!PyArg_ParseTuple(args, "ss", &src, &dst)) {
        return NULL;
    }

    Result res = rename_item(src, dst);
    return Py_BuildValue("(is)", (int)res, "");
}

static PyObject *method_rmdir(PyObject *self, PyObject *args) {
    const char *path;
    int force = 0;
    if (!PyArg_ParseTuple(args, "s|p", &path, &force)) {
        return NULL;
    }

    Result res = remove_dir(path, force != 0);
    return Py_BuildValue("(is)", (int)res, "");
}

static PyObject *method_rm(PyObject *self, PyObject *args) {
    const char *path;
    int recursive = 0;
    if (!PyArg_ParseTuple(args, "s|p", &path, &recursive)) {
        return NULL;
    }

    Result res = remove_item(path, recursive != 0);
    return Py_BuildValue("(is)", (int)res, "");
}

static PyMethodDef DiskopsMethods[] = {
    {"ping", method_ping, METH_NOARGS, "Health check ping."},
    {"cat", method_cat, METH_VARARGS, "Read file content natively."},
    {"touch", method_touch, METH_VARARGS, "Touch or create file natively."},
    {"dir", method_dir, METH_VARARGS, "List directory contents natively."},
    {"mkdir", method_mkdir, METH_VARARGS, "Create directory natively."},
    {"rename", method_rename, METH_VARARGS, "Rename file or directory natively."},
    {"rmdir", method_rmdir, METH_VARARGS, "Remove directory natively."},
    {"rm", method_rm, METH_VARARGS, "Remove file or directory natively."},
    {NULL, NULL, 0, NULL},
};

static struct PyModuleDef diskopsmodule = {PyModuleDef_HEAD_INIT, "_native_diskops",
                                           "Flyshell native disk operations.", -1, DiskopsMethods};

PyMODINIT_FUNC PyInit__native_diskops(void) {
    return PyModule_Create(&diskopsmodule);
}
