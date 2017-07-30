#include "color_reducer.hpp"
#define THRESHOLD 50
#include <utility>
#include <cmath>

Graph* Graph::create_child(color_id_t removed_color) {
    Graph* new_graph = new Graph(removed_colors, removed_color);
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

Graph* create_graph(std::vector<Color>& colors) {
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

std::vector<color_id_t>* Graph::explore_graph() {
    if (!are_nodes_linked())
        return &removed_colors;

    std::vector<color_id_t>* removed_tmp;
    std::vector<color_id_t>* colors_removed;
    uint32_t min_size = -1;
    for (auto& l : lists) {
        if (l.second.empty())
            continue;
        Graph* child = create_child(l.first);
        removed_tmp = child->explore_graph();
        if (removed_tmp->size() < min_size) {
            colors_removed = removed_tmp;
            min_size = removed_tmp->size();
        }
    }
    return colors_removed;
}

void solve_problem(std::vector<Color>& colors) {

    Graph* graph = create_graph(colors);

    if (!graph->are_nodes_linked()) {
        std::cout << "No colors to be removed" << std::endl;
        return;
    }

    std::vector<color_id_t>* colors_removed = graph->explore_graph();

    std::cout << "Finished exploring, the smallest set is: ";
    for (auto& c : *colors_removed) {
        std::cout << c << ", ";
    }
    std::cout << std::endl;
    free_graphs(graph);
}

uint32_t distance(const Color& c1, const Color& c2) {
    if (c1.value > c2.value)
        return c1.value - c2.value;
    return c2.value - c1.value;
}

bool Color::operator!=(const Color& c) const {
    if (c.id != id)
        return true;
    return false;
}

int main() {
    std::vector<Color> colors;
    colors.push_back(Color(1, 0));
    colors.push_back(Color(2, 30));
    colors.push_back(Color(3, 70));
    colors.push_back(Color(4, 100));
    colors.push_back(Color(5, 140));

    solve_problem(colors);
    return 0;
}

std::ostream& operator<<(std::ostream& out, const Graph& graph) {
    for (const auto& it : graph.lists) {
        out << "List " 
            << it.first 
            << " size: " << it.second.color_list.size() << std::endl;
    }
    return out;
}

void free_graphs(Graph* root) {
    auto it = root->children_begin();
    while (it != root->children_end()) {
        free_graphs(*it);
        it++;
    }
    delete root;
}
