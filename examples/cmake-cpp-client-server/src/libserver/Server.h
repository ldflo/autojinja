#pragma once

/// @brief Server object that listens for function calls through shared memory.
///
class Server {
public:
    /// @brief Runs the server in the current thread
    void run();
    /// @brief Stops the server
    void stop();

protected:
    /// @brief Reads the content of the shared memory and performs the
    ///        appropriate function call with the provided parameters.
    ///        The result is then written back to the shared memory.
    void call();

    volatile bool _stop = false;
};
