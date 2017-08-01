#include "color_reducer.hpp"
#define THRESHOLD 300
#include <utility>
#include <cmath>

uint32_t Color::next_id = 0;

static uint32_t distance(const Color& c1, const Color& c2);

static void free_graphs(Graph* root);

/////////////////////////////////////
////////////// GRAPH ////////////////
/////////////////////////////////////
Graph* Graph::create_child(color_id_t removed_color) {
    Graph* new_graph = new Graph(this, removed_color);
    for (auto& l : lists) {
        if (l.first != removed_color) {
            List new_list (l.second);
            new_list.remove(removed_color);
            std::pair<const color_id_t, List> p(new_list.id, new_list);
            new_graph->lists.insert(p);
        }
    }
    children.push_back(new_graph);
    return children.back();
}

bool Graph::are_nodes_linked() {
    for (auto& l : lists) {
        if (!l.second.empty())
            return true;
    }
    return false;
}

std::vector<color_id_t>* Graph::explore_graph() {
    if (!are_nodes_linked())
        return &removed_colors;
    if (get_optimal_length() != (uint16_t)(-1)
            && removed_colors.size() > get_optimal_length())
        return nullptr;

    std::vector<color_id_t>* removed_tmp;
    std::vector<color_id_t>* opt_removal;
    for (auto& l : lists) {
        if (l.second.empty())
            continue;
        Graph* child = create_child(l.first);
        removed_tmp = child->explore_graph();
        if (removed_tmp != nullptr 
                && removed_tmp->size() < get_optimal_length()) {
            opt_removal = removed_tmp;
            set_optimal_length(removed_tmp->size());
        }
    }
    return opt_removal;
}

/////////////////////////////////////
//////// STATIC FUNCTIONS ///////////
/////////////////////////////////////
//
static Graph* create_graph(const std::vector<Color>& colors) {
    Graph* graph = new Graph();
    for (const auto& c1 : colors) {
        for (const auto& c2 : colors) {
            uint32_t dist = distance(c1, c2);
            if (c1 != c2 &&  dist < THRESHOLD) {
                graph->append_node(c1.id, c2.id);
            }
        }
    }
    return graph;
}


bool in_vector(color_id_t val, std::vector<color_id_t>& vect) {
    for (const auto& c : vect) {
        if (val == c)
            return true;
    }
    return false;
}

void encode_color(char* output_string, color_type_t color) {
    output_string[0] = color.l;
    output_string[1] = color.a;
    output_string[2] = color.b;
}

void encode_colors(std::vector<color_id_t>& opt_removal,
                      std::vector<Color>& input_colors,
                      char* output_string) {

    uint16_t i = 0;
    for (const auto& c_in : input_colors) {
        if (!in_vector(c_in.id, opt_removal)) {
            encode_color(&(output_string[i * 3]), c_in.value);
            i++;
        }
    }
    output_string[i * 3] = '\0';
}

void decode_colors(
        char* input_string, std::vector<Color>& input_colors) {
    uint32_t i = 0;
    while (input_string[i] != '\0') {
        Color c(&(input_string[i]));
        input_colors.push_back(c);
        i += 3;
    }
}

void reduce_colors(char* input_string, char* output_string) {

    std::vector<Color> input_colors;
    decode_colors(input_string, input_colors);

    Graph* graph = create_graph(input_colors);
    /* std::cout << *graph << std::endl; */

    std::vector<color_id_t>* opt_removal = graph->explore_graph();

    /* std::cout << "Finished exploring, the smallest set is: "; */
    /* for (auto& c : *opt_removal) { */
    /*     std::cout << c << ", "; */
    /* } */
    /* std::cout << std::endl; */

    encode_colors(*opt_removal, input_colors, output_string);

    free_graphs(graph);

}

uint32_t distance(const Color& c1, const Color& c2) {
    return std::pow(c1.value.l - c2.value.l, 2) 
                + std::pow(c1.value.a - c2.value.a, 2)
                + std::pow(c1.value.b - c2.value.b, 2);
}

bool Color::operator!=(const Color& c) const {
    if (c.id != id)
        return true;
    return false;
}

void free_graphs(Graph* root) {
    auto it = root->children_begin();
    while (it != root->children_end()) {
        free_graphs(*it);
        it++;
    }
    delete root;
}

std::ostream& operator<<(std::ostream& out, const List& l) {
    std::cout << l.id << " : ";
    for (const auto& e : l.color_list) {
        std::cout << " " << e;
    }
    std::cout << std::endl;
    return out;
}

std::ostream& operator<<(std::ostream& out, const Graph& graph) {
    for (const auto& it : graph.lists) {
        out << it.second;
    }
    return out;
}
