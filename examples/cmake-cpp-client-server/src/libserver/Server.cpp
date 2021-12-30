#include "Server.h"

#include "ServerApi.h"
#include "shared_memory.h"

/// @brief Runs the server in the current thread
void Server::run() {
    std::unique_lock<std::mutex> lock(shared_memory::mutex);
    _stop = false;
    do {
        if (shared_memory::size() > 0) {
            call(); // Perform function call
            shared_memory::cv.notify_one(); // Notify result
        }
        shared_memory::cv.wait(lock); // Wait for incomming calls
    } while (!_stop);
}

/// @brief Stops the server
void Server::stop() {
    std::unique_lock<std::mutex> lock(shared_memory::mutex);
    _stop = true;
    shared_memory::cv.notify_all();
}

/// @brief Reads the content of the shared memory and performs the
///        appropriate function call with the provided parameters.
///        The result is then written back to the shared memory.
void Server::call() {
    char* ptr = shared_memory::buffer;
    switch (deserialize<unsigned int>(ptr)) {
        // [[[ {{ '\n'.join(server_impls) }} ]]]
        case 1u: { /* add */
            int arg1 = deserialize<int>(ptr);
            float arg2 = deserialize<float>(ptr);
            float result = ServerApi::add(arg1, arg2);
            shared_memory::clear();
            serialize(result, shared_memory::ptr);
        } break;
        case 2u: { /* strip */
            std::string str = deserialize<std::string>(ptr);
            std::string result = ServerApi::strip(str);
            shared_memory::clear();
            serialize(result, shared_memory::ptr);
        } break;
        case 3u: { /* tochars */
            std::string str = deserialize<std::string>(ptr);
            std::vector<char> result = ServerApi::tochars(str);
            shared_memory::clear();
            serialize(result, shared_memory::ptr);
        } break;
        case 4u: { /* fromchars */
            std::vector<char> vector = deserialize<std::vector<char>>(ptr);
            std::string result = ServerApi::fromchars(vector);
            shared_memory::clear();
            serialize(result, shared_memory::ptr);
        } break;
        // [[[ end ]]]
    }
}
