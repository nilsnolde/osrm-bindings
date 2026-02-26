#include "types/jsoncontainer_nb.h"

#include "util/json_container.hpp"

#include <nanobind/nanobind.h>
#include <nanobind/make_iterator.h>
#include <nanobind/stl/string.h>
#include <nanobind/stl/string_view.h>

namespace nb = nanobind;
namespace json = osrm::util::json;

void init_JSONContainer(nb::module_& m) {
    nb::class_<json::Object>(m, "Object")
        .def(nb::init<>())
        .def("__len__", [](const json::Object& obj) {
            return obj.values.size();
        })
        .def("__bool__", [](const json::Object& obj) {
            return !obj.values.empty();
        })
        .def("__repr__", [](const json::Object& obj) {
            ValueStringifyVisitor visitor;
            return visitor.visitobject(obj);
        })
        .def("__getitem__", [](json::Object& obj, const std::string& key) {
            return obj.values.at(key);
        })
        .def("__contains__", [](const json::Object& obj, const std::string& key) {
            return obj.values.count(key) > 0;
        })
        .def("__iter__", [m](const json::Object& obj) {
            return nb::make_key_iterator(m, "key_iterator",
                                        obj.values.begin(), obj.values.end());
        }, nb::keep_alive<0, 1>());

    nb::class_<json::Array>(m, "Array")
        .def(nb::init<>())
        .def("__len__", [](const json::Array& arr) {
            return arr.values.size();
        })
        .def("__bool__", [](const json::Array& arr) {
            return !arr.values.empty();
        })
        .def("__repr__", [](const json::Array& arr) {
            ValueStringifyVisitor visitor;
            return visitor.visitarray(arr);
        })
        .def("__getitem__", [](json::Array& arr, int i) {
            return arr.values[i];
        })
        .def("__iter__", [m](const json::Array& arr) {
            return nb::make_iterator(m, "value_iterator",
                                    arr.values.begin(), arr.values.end());
        }, nb::keep_alive<0, 1>());

    nb::class_<json::String>(m, "String")
        .def(nb::init<std::string>());
    nb::class_<json::Number>(m, "Number")
        .def(nb::init<double>());

    nb::class_<json::True>(m, "True")
        .def(nb::init<>());
    nb::class_<json::False>(m, "False")
        .def(nb::init<>());
    nb::class_<json::Null>(m, "Null")
        .def(nb::init<>());
}
