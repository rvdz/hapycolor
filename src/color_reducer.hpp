#include <iostream>
#include <vector>
#include <map>
#include <list>
#include <cstdint>

typedef uint32_t color_id_t;

struct Color {
    color_id_t id;
    // The value could be in hsl format or rgb
    uint32_t value;

    Color(color_id_t col_id, uint32_t val) : id(col_id), value(val) {}

    bool operator!=(const Color& other) const;
};

struct List {
    color_id_t id;
    std::list<color_id_t> color_list;

    List(const List& list) : id(list.id), color_list(list.color_list) { }
    List(color_id_t id)  : id(id) {}

    void remove(color_id_t color_id) {
        color_list.remove(color_id);
    }
    void push_back(color_id_t color_id) {
        color_list.push_back(color_id);
    }

    bool empty() {
        return color_list.empty();
    }
};

// The lists are indexed by their list_id
struct Graph {
private:
    std::vector<color_id_t> removed_colors;
    std::vector<Graph*> children;
    std::map<color_id_t, List> lists;

public:
    Graph* create_child(color_id_t removed_color);
    bool are_nodes_linked();

    std::vector<Graph*>::iterator children_begin() {
        return children.begin();
    }

    std::vector<Graph*>::iterator children_end() {
        return children.end();
    }

    void append_node(color_id_t src_color, color_id_t dst_color) {
        List l (src_color);
        l.push_back(dst_color);
        lists.insert(std::make_pair(src_color, l));
    }

    void append_child(Graph* child) {
        children.push_back(child);
    }

    std::vector<color_id_t>* explore_graph();

    Graph() {}
    
    Graph(std::vector<color_id_t> rm_colors, color_id_t rm_color)
        : removed_colors(rm_colors) {
        this->removed_colors.push_back(rm_color);
    }

    ~Graph() = default;

    friend std::ostream& operator<<(std::ostream& out, const Graph& graph);
};

uint32_t distance(const Color& c1, const Color& c2);

void free_graphs(Graph* root);

