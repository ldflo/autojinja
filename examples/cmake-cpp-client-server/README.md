# C++ client / server example with CMake

This example generates a server and a client that will communicate through a shared memory, starting from the API described in the `xml/server.xml` file. To minimize the dependencies of this example, the client and the server are in fact both compiled into the same binary, and the shared memory is emulated thanks to a static byte array instead.

The whole CMake project is separated into targets that execute the **autojinja** command to perform generation of their local files :

```
src/libtransport/
  | static library with the shared memory and serialization functions

src/libserver/
  | static library of the server API
  | uses libtransport to answer incoming calls through the shared memory
  | uses autojinja

src/libclient/
  | static library of the client API
  | uses libtransport to make calls through the shared memory
  | uses autojinja

src/apps/
  | final executable
  | uses libserver and libclient
```

## Server

Each item in the XML file...

```xml
<Function name="add">
    <Description value="Returns arg1 + arg1"/>
    <ReturnType type="float"/>
    <Arg name="arg1" type="int"/>
    <Arg name="arg2" type="float" default="0.1f"/>
</Function>
```

...will be generated in `src/libserver/ServerApi.h` and `src/libserver/ServerApi.cpp` as a global function...

```cpp
/// @brief Returns arg1 + arg1
float add(int arg1, float arg2) {
    // <<[ impl_add ]>>
    static_assert(false, "ServerApi::add is not implemented...");
    // <<[ end ]>>
}
```

...whose input parameters are deserialized in `src/libserver/Server.cpp`, and its result written back into the shared memory :

```cpp
switch (deserialize<unsigned int>(ptr)) {
    // [[[ {{ '\n'.join(server_impls) }} ]]]
    case 1u: { /* add */
        int arg1 = deserialize<int>(ptr);
        float arg2 = deserialize<float>(ptr);
        float result = ServerApi::add(arg1, arg2);
        shared_memory::clear();
        serialize(result, shared_memory::ptr);
    } break;
    ...
    // [[[ end ]]]
}
```

The implementation of the server API can then be manually provided within the dedicated sections.

## Client

Each item in the XML file...

```xml
<Function name="strip">
    <Description value="Strips whitespaces, tabulations and end-of-lines"/>
    <ReturnType type="std::string"/>
    <Arg name="str" type="const std::string&amp;"/>
</Function>
```

...will be generated in `src/libclient/ClientApi.h` and `src/libclient/ClientApi.cpp` as a ready-to-use function that performs a server call through the shared memory :

```cpp
/// @brief Strips whitespaces, tabulations and end-of-lines
std::string strip(const std::string& str) {
    std::unique_lock<std::mutex> lock(shared_memory::mutex);
    shared_memory::clear();
    serialize(2u /* strip */, shared_memory::ptr);
    serialize(str, shared_memory::ptr);
    shared_memory::cv.notify_one(); // Send parameters
    shared_memory::cv.wait(lock); // Wait for result
    char* ptr = shared_memory::buffer;
    return deserialize<std::string>(ptr);
}
```

## Environment variables

Both the client and the server use environment variables defined inside the `autojinja.env` file :

- `SERVER_XML` environment variable : indicates where to find the XML file
- `PYTHONPATH` environment variable : allows to directly import all Python scripts located in the `utility/` directory

# Dependencies

All dependencies required for this example can be installed with the command :

```shell
$ pip install requirements.txt
```

# How to execute

The whole generation process takes place in `src/libserver/__jinja__.py` and `src/libclient/__jinja__.py` scripts, which are automatically executed by CMake when needed. With Visual Studio Code and the CMake extension, CMake configuration and compilation is triggered by pressing the `F7` key.

The final binary containing the server and the client can be executed with the command :

On Windows (MSVC compiler) :

```shell
$ ./build/src/app/Debug/app.exe
```

On Unix (GCC compiler) :

```shell
$ ./build/src/app/app
```

# CMake and **autojinja**

The **autojinja** command is made available within `CMakeLists.txt` files by including the [`autojinja.cmake`](https://github.com/ldflo/autojinja/blob/main/examples/cmake-cpp-client-server/autojinja.cmake) file, which enables creating **autojinja** targets in all CMake subdirectories, as well as listing all target dependencies so that CMake re-executes the command when such dependencies change (XML files, additional scripts, etc...) :

```cmake
include(autojinja.cmake)
```

An **autojinja** target can then be created by listing all the generation scripts to execute, as well as the files they generate so that they can be part of the compilation process :

```cmake
autojinja(__jinja__.py GENERATES file.h file.cpp)

add_library(mylib STATIC ${autojinja}) # The ${autojinja} variable contains "file.h file.cpp"
```
