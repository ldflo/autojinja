#include "serializer.h"

/// @brief ServerApi.h
///        Below content is entirely generated.
///
namespace ServerApi {
    // [[[ {{ '\n'.join(api_defs) }} ]]]
    /// @brief Returns arg1 + arg1
    float add(int arg1, float arg2 = 0.1f);
    /// @brief Strips whitespaces, tabulations and end-of-lines
    std::string strip(const std::string& str);
    /// @brief Returns a vector containing each character of the given string
    std::vector<char> tochars(const std::string& str);
    /// @brief Returns the string of the given character vector
    std::string fromchars(const std::vector<char>& vector);
    // [[[ end ]]]
}
