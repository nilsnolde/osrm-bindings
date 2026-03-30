cmake_minimum_required(VERSION 3.28)

set(PROJECT_NAME "osrm")
set(EXT_NAME "osrm_ext")
project(${PROJECT_NAME} LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if(NOT SKBUILD)
  message(WARNING
  "This CMake file is meant to be executed using 'scikit-build-core'.
  Running it directly might not produce the desired
  result. If you are a user trying to install this package, use the
  command below, which will install all necessary build dependencies,
  compile the package in an isolated environment, and then install it.
  =====================================================================
   $ pip install .
  ====================================================================="
  )
endif()

if (NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
  set(CMAKE_BUILD_TYPE Release CACHE STRING "Choose the type of build." FORCE)
  set_property(CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS "Debug" "Release" "MinSizeRel" "RelWithDebInfo")
endif()

find_package(Python
  REQUIRED COMPONENTS Interpreter Development.Module
  OPTIONAL_COMPONENTS Development.SABIModule
)

# find the python nanobind's cmake dir and use it
execute_process(
  COMMAND "${Python_EXECUTABLE}" -m nanobind --cmake_dir
  OUTPUT_STRIP_TRAILING_WHITESPACE OUTPUT_VARIABLE NB_DIR
)
list(APPEND CMAKE_PREFIX_PATH "${NB_DIR}")
find_package(nanobind CONFIG REQUIRED)

set(SRCS
  src/osrm_nb.cpp
  src/engineconfig_nb.cpp
  src/utility/osrm_utility.cpp
  src/utility/param_utility.cpp

  src/parameters/baseparameter_nb.cpp
  src/parameters/routeparameter_nb.cpp
  src/parameters/matchparameter_nb.cpp
  src/parameters/nearestparameter_nb.cpp
  src/parameters/tableparameter_nb.cpp
  src/parameters/tileparameter_nb.cpp
  src/parameters/tripparameter_nb.cpp
  
  src/types/optional_nb.cpp
  src/types/coordinate_nb.cpp
  src/types/jsoncontainer_nb.cpp
  src/types/approach_nb.cpp
  src/types/bearing_nb.cpp
)
nanobind_add_module(
  ${EXT_NAME}
  STABLE_ABI
  NB_STATIC
  LTO
  ${SRCS}
)

target_include_directories(${EXT_NAME} 
  PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/include)

# use OSRM upstream's FindLibOSRM.cmake
list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/cmake)
find_package(LibOSRM)

if(LibOSRM_FOUND)
  target_link_libraries(${EXT_NAME}
    PRIVATE
      ${LibOSRM_LIBRARIES}
      ${LibOSRM_DEPENDENT_LIBRARIES}
      Python::SABIModule
  )
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${LibOSRM_CXXFLAGS}")

  file(GLOB OSRM_EXECS ${LibOSRM_EXEC_DIR}/osrm-*)
  install(FILES ${OSRM_EXECS} TYPE BIN 
          PERMISSIONS OWNER_WRITE OWNER_READ GROUP_READ WORLD_READ 
          OWNER_EXECUTE GROUP_EXECUTE WORLD_EXECUTE)
else()
  include(FetchContent)
  FetchContent_Declare(
    libosrm
    GIT_REPOSITORY ${OSRM_GIT_REPO}
    GIT_TAG ${OSRM_GIT_TAG}
    EXCLUDE_FROM_ALL
    # Make all conan deps static for self-contained wheels (not appropriate for upstream OSRM)
    PATCH_COMMAND patch -p1 -N -i ${CMAKE_SOURCE_DIR}/patches/conan-static-deps.patch
  )
  # Suppress GCC/Clang warnings from OSRM code (not valid for MSVC)
  if (NOT MSVC)
    SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wno-array-bounds -Wno-uninitialized -Wno-free-nonheap-object")
  endif()

  set(CMAKE_INSTALL_PREFIX ${CMAKE_CURRENT_BINARY_DIR})
  set(FETCHCONTENT_QUIET OFF)
  # Ensure ENABLE_CONAN is forwarded to OSRM's CMakeLists.txt (Windows conan builds)
  if(ENABLE_CONAN)
    set(ENABLE_CONAN ON CACHE BOOL "" FORCE)
  endif()
  FetchContent_MakeAvailable(libosrm)

  target_include_directories(${EXT_NAME}
    PUBLIC
      ${libosrm_SOURCE_DIR}/include
      ${libosrm_SOURCE_DIR}/third_party/variant/include
      ${libosrm_SOURCE_DIR}/third_party/flatbuffers/include
  )
  target_link_libraries(${EXT_NAME}
    PRIVATE
      osrm
      Python::SABIModule
  )

  # EXCLUDE_FROM_ALL skips OSRM's install rules, so these targets won't build
  # unless explicitly depended on. We need the executables and profiles in the wheel.
  set(OSRM_EXECUTABLES osrm-extract osrm-contract osrm-customize osrm-partition osrm-datastore osrm-routed osrm-components)
  add_dependencies(${EXT_NAME} ${OSRM_EXECUTABLES})
  install(TARGETS ${OSRM_EXECUTABLES} DESTINATION bin)
  install(DIRECTORY ${libosrm_SOURCE_DIR}/profiles DESTINATION share/osrm)
endif()

if (MSVC)
  add_definitions(-DBOOST_ALL_NO_LIB)
endif()

install(TARGETS ${EXT_NAME} LIBRARY DESTINATION ${PROJECT_NAME})

# Generate Python type stubs (.pyi) from the compiled extension module.
# Stubs are written to the source tree so they can be committed and used by
# mkdocstrings to build docs without compiling the extension.
# CI verifies committed stubs are up to date (see check_stubs job).
nanobind_add_stub(
  ${EXT_NAME}_stub
  MODULE osrm_ext
  OUTPUT ${PROJECT_SOURCE_DIR}/src/osrm/osrm_ext.pyi
  PYTHON_PATH $<TARGET_FILE_DIR:${EXT_NAME}>
  DEPENDS ${EXT_NAME}
)
