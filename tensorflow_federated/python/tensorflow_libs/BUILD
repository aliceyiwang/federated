package(default_visibility = ["//tensorflow_federated:__subpackages__"])

licenses(["notice"])  # Apache 2.0

py_library(
    name = "tensorflow_libs",
    srcs = ["__init__.py"],
)

py_library(
    name = "tensor_utils",
    srcs = ["tensor_utils.py"],
    deps = ["//tensorflow_federated/python/common_libs:py_typecheck"],
)

py_test(
    name = "tensor_utils_test",
    size = "small",
    srcs = ["tensor_utils_test.py"],
    deps = [
        ":tensor_utils",
        "//tensorflow_federated/python/common_libs:test",
    ],
)

py_library(
    name = "graph_keys",
    srcs = ["graph_keys.py"],
)
