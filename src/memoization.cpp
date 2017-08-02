#include "memoization.hpp"


void ComputedGraphs::add_result(const ByteVector& graph_colors,
                                 const std::vector<color_id_t>& removed_colors) {
  computedGraphs.insert(std::pair<ByteVector,
                                  std::vector<color_id_t>>(graph_colors,removed_colors));
}

std::vector<color_id_t>& ComputedGraphs::get_result(const ByteVector& graph_colors) const {
  std::map<ByteVector, std::vector<color_id_t>>::iterator it = computedGraphs.find(graph_colors);
  if (it == computedGraphs.end())
    return std::vector<color_id_t>();
  return it->second;
}

// Add level counter to graph class
// Do not down propagate removed colors, only up. After exploring, returns removed colors +
// current removed color
// Graph object contains a ByteVector representing the nodes of the current graph
