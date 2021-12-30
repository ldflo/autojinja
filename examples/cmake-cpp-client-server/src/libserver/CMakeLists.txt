autojinja(__jinja__.py GENERATES ServerApi.cpp Server.cpp)

add_library(libserver STATIC ${autojinja})
target_include_directories(libserver PUBLIC .)
target_link_libraries(libserver PUBLIC libtransport)
