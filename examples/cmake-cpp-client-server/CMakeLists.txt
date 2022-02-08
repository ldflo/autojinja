cmake_minimum_required(VERSION 3.11)

### autojinja functions
include(autojinja.cmake)

### autojinja environment
autojinja_environment(autojinja.env)
autojinja_dependencies(utility/**)

### project
project(cmake-cpp-client-server LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
add_subdirectory(src)
