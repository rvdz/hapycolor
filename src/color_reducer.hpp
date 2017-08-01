#include <iostream>
#include <vector>
#include <map>
#include <list>
#include <cstdint>

typedef uint32_t color_id_t;

struct LAB {
    uint8_t l;
    uint8_t a;
    uint8_t b;

    LAB(char l, char a, char b) {
        this->l = l;
        this->a = a;
        this->b = b;
    }
};

typedef LAB color_type_t;

struct Color {
    static uint32_t next_id;
    color_id_t id;
    color_type_t value;

    Color(char* val) : id(next_id++), value(val[0], val[1], val[2]) {}

    std::ostream& operator<<(std::ostream& out) const {
        out << "(Id: " << id << ", Value: " << value.a << ")" << std::endl;
        return out;
    }

    bool operator!=(const Color& other) const;
};

struct List {
    color_id_t id;
    std::list<color_id_t> color_list;

    List(const List& list) : id(list.id), color_list(list.color_list) { }
    List(color_id_t id)  : id(id) {}

    uint32_t size() const { return color_list.size(); }

    void remove(color_id_t color_id) {
        color_list.remove(color_id);
    }
    void push_back(color_id_t color_id) {
        color_list.push_back(color_id);
    }

    bool empty() {
        return color_list.empty();
    }

    friend std::ostream& operator<<(std::ostream& out, const List& l);
};

// The lists are indexed by their list_id
struct Graph {
private:
    std::vector<color_id_t> removed_colors;
    std::vector<Graph*> children;
    uint16_t opt_solution_length;
    std::map<color_id_t, List> lists;

public:
    Graph* create_child(color_id_t removed_color);
    bool are_nodes_linked();

    void set_optimal_length(uint16_t opt_solution_length) {
        this->opt_solution_length = opt_solution_length;
    }

    uint16_t get_optimal_length() { return opt_solution_length; }

    std::vector<Graph*>::iterator children_begin() {
        return children.begin();
    }

    std::vector<Graph*>::iterator children_end() {
        return children.end();
    }

    void append_node(color_id_t src_color, color_id_t dst_color) {
        try {
            lists.at(src_color).push_back(dst_color);
        } catch (std::out_of_range oor) {
            List l (src_color);
            l.push_back(dst_color);
            lists.insert(std::make_pair(src_color, l));
        }
    }

    void append_child(Graph* child) {
        children.push_back(child);
    }

    std::vector<color_id_t>* explore_graph();

    Graph() : opt_solution_length(-1) {}
    
    Graph(Graph* graph, color_id_t rm_color)
        : removed_colors(graph->removed_colors),  
          opt_solution_length(graph->opt_solution_length)
    {
        this->removed_colors.push_back(rm_color);
    }

    ~Graph() = default;

    friend std::ostream& operator<<(std::ostream& out, const Graph& graph);
};

extern "C" {
    void reduce_colors(char* input_string, char* output_string);
}
