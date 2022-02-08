autojinja(__jinja__.py 
    GENERATES 
        ClientApi.cpp 
    DEPENDS 
        "${XML_DIRPATH}/**"
)

add_library(libclient STATIC ${autojinja})
target_include_directories(libclient PUBLIC .)
target_link_libraries(libclient PUBLIC libtransport)
