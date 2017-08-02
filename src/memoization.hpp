typedef uint32_t ByteVector;
typedef uint32_t color_id_t;

class ComputedGraphs {
private:
  std::map<ByteVector, std::vector<color_id_t>> computedGraphs;

public:
  void add_result(const ByteVector& graph_colors, const std::vector<color_id_t>& removed_colors);
  std::vector<color_id_t>& ComputedGraphs::get_result(const ByteVector& graph_colors) const;
}
