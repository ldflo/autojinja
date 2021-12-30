#include "ServerApi.h"
#include <iostream>

/// @brief Implementation of ServerApi.h.
///        Below content is generated and implementations are manually provided.
///
namespace ServerApi {
    // [[[ {{ '\n'.join(api_impls) }} ]]]
    /// @brief Returns arg1 + arg1
    float add(int arg1, float arg2) {
        // <<[ impl_add ]>>
        return arg1 + arg2;
        // <<[ end ]>>
    }
    /// @brief Strips whitespaces, tabulations and end-of-lines
    std::string strip(const std::string& str) {
        // <<[ impl_strip ]>>
        size_t start = 0;
        size_t end = str.size();
        for (; start < end; ++start)
            switch (str[start]) {
                case ' ': case '\t': case '\n': case '\r': break;
                default: goto break1;
            } break1:
        for (; end > start; --end)
            switch (str[end]) {
                case ' ': case '\t': case '\n': case '\r': break;
                default: goto break2;
            } break2:
        return str.substr(start, end-start);
        // <<[ end ]>>
    }
    /// @brief Returns a vector containing each character of the given string
    std::vector<char> tochars(const std::string& str) {
        // <<[ impl_tochars ]>>
        std::vector<char> result(str.size());
        for (size_t i = 0; i < str.size(); ++i)
            result[i] = str[i];
        return result;
        // <<[ end ]>>
    }
    /// @brief Returns the string of the given character vector
    std::string fromchars(const std::vector<char>& vector) {
        // <<[ impl_fromchars ]>>
        std::string result(vector.size(), 0);
        for (size_t i = 0; i < vector.size(); ++i)
            result[i] = vector[i];
        return result;
        // <<[ end ]>>
    }
    // [[[ end ]]]
}
