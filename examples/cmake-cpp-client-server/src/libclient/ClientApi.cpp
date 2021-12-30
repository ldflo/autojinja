#include "ClientApi.h"

#include "shared_memory.h"

/// @brief Implementation of ClientApi.h.
///        Below content is entirely generated.
///
namespace ClientApi {
    // [[[ {{ '\n'.join(api_impls) }} ]]]
    /// @brief Returns arg1 + arg1
    float add(int arg1, float arg2) {
        std::unique_lock<std::mutex> lock(shared_memory::mutex);
        shared_memory::clear();
        serialize(1u /* add */, shared_memory::ptr);
        serialize(arg1, shared_memory::ptr);
        serialize(arg2, shared_memory::ptr);
        shared_memory::cv.notify_one(); // Send parameters
        shared_memory::cv.wait(lock); // Wait for result
        char* ptr = shared_memory::buffer;
        return deserialize<float>(ptr);
    }
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
    /// @brief Returns a vector containing each character of the given string
    std::vector<char> tochars(const std::string& str) {
        std::unique_lock<std::mutex> lock(shared_memory::mutex);
        shared_memory::clear();
        serialize(3u /* tochars */, shared_memory::ptr);
        serialize(str, shared_memory::ptr);
        shared_memory::cv.notify_one(); // Send parameters
        shared_memory::cv.wait(lock); // Wait for result
        char* ptr = shared_memory::buffer;
        return deserialize<std::vector<char>>(ptr);
    }
    /// @brief Returns the string of the given character vector
    std::string fromchars(const std::vector<char>& vector) {
        std::unique_lock<std::mutex> lock(shared_memory::mutex);
        shared_memory::clear();
        serialize(4u /* fromchars */, shared_memory::ptr);
        serialize(vector, shared_memory::ptr);
        shared_memory::cv.notify_one(); // Send parameters
        shared_memory::cv.wait(lock); // Wait for result
        char* ptr = shared_memory::buffer;
        return deserialize<std::string>(ptr);
    }
    // [[[ end ]]]
}
