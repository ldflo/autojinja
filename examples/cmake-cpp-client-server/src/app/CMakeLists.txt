find_package(Threads REQUIRED)
add_executable(app main.cpp)
target_link_libraries(app PUBLIC libclient libserver Threads::Threads)
