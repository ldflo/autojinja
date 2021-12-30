#pragma once

#include <cstring>
#include <condition_variable>
#include <mutex>

/// @brief Static buffer to emulate a shared memory.
///
struct shared_memory {
    /// Mutex
    static std::mutex mutex;
    static std::condition_variable cv;

    /// Buffer
    static constexpr size_t length = 8192;
    static char buffer[length];
    static char* ptr;

    static inline size_t size() {
        return ptr - buffer;
    }
    static inline size_t remaining() {
        return length - size();
    }
    static inline void clear() {
        std::memset(buffer, 0, size());
        ptr = buffer;
    }
};
