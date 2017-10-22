/*
    Copyright 2007-2012 Janez Konc

    If you use this program, please cite:
    Janez Konc and Dusanka Janezic. An improved branch and bound algorithm for the
    maximum clique problem. MATCH Commun. Math. Comput. Chem., 2007, 58, 569-590.

    More information at: http://www.sicmm.org/~konc

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

#include <fstream>
#include <iostream>
#include <set>
#include <string.h>
#include <map>
#include <assert.h>
#include "mcqd.h"
#include <cmath>
#include <cwchar>

extern "C" {
  void reduce(wchar_t* input_char, uint32_t length, wchar_t* output_char);
}

using namespace std;

/**
 * Decodes the input string and then populates the data structure used to solve the maximal clique problem
 */
void read_colors(wchar_t* input_char, uint32_t length, bool** &conn, int &size) {
  set<int> v;
  multimap<int,int> e;

  for (uint32_t i = 0; i < length; i++) {
    int vi = static_cast<uint32_t>(input_char[i * 2]);
    int vj = static_cast<uint32_t>(input_char[i * 2 + 1]);

    assert(vi >= 0 && vj >= 0);
    v.insert(vi);
    v.insert(vj);
    e.insert(make_pair(vi, vj));
  }

//  size = v.size() + 1;
  size = *v.rbegin() + 1;
  conn = new bool*[size];
  for (int i=0; i < size; i++) {
    conn[i] = new bool[size];
    memset(conn[i], 0, size * sizeof(bool));
  }

  for (multimap<int,int>::iterator it = e.begin(); it != e.end(); it++) {
    assert(0 <= it->first && it->first < size
           && 0 <= it->second && it->second < size);
    conn[it->first][it->second] = true;
    conn[it->second][it->first] = true;
  }
}

void write_colors(int* results, int size, wchar_t* output_char) {
  for (int i = 0; i < size; i++) {
      output_char[i] = results[i];
  }
}

/**
 * Finds the maximal clique for a given graph
 * @param input_char  an encoded string containing the graph
 * @param length      the number of couple of vertices in the graph having a common edge
 * @param output_char the string in which the encoded result will be stored
 */
void reduce(wchar_t* input_char, uint32_t length, wchar_t* output_char) {
  bool **conn;
  int size;
  read_colors(input_char, length, conn, size);

  Maxclique m(conn, size);
  int *qmax;
  int qsize;
  m.mcq(qmax, qsize);

  write_colors(qmax, qsize, output_char);

  delete [] qmax;
}
