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

extern "C" {
  void color_reducer(char* input_char, uint32_t length, char* output_char);
}

using namespace std;
        
/**
 * Decode a string where an integer is encoded over four bytes. The even ones
 * contain either '\x01' or '\x02' if the following value is null. The odd
 * ones contain a dummy value if it should be null, or the actual value 
 * Then populates the data structure used to solve the maximal clique problem
 */
void read_colors(char* input_char, uint32_t length, bool** &conn, int &size) {
  set<int> v;
  multimap<int,int> e;
  for (uint32_t i = 0; i < length; i++) {
    int vi = 0;
    if ((uint8_t)(input_char[i * 8]) == 2)
        vi += (uint8_t)(input_char[i * 8 + 1]) << 8;

    if ((uint8_t)(input_char[i * 8 + 2]) == 2)
        vi += (uint8_t)(input_char[i * 8 + 3]);


    int vj = 0;
    if ((uint8_t)(input_char[i * 8 + 4]) == 2)
        vj += (uint8_t)(input_char[i * 8 + 5]) << 8;

    if ((uint8_t)(input_char[i * 8 + 6]) == 2)
        vj += (uint8_t)(input_char[i * 8 + 7]);

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
  
/**
 * Finds the maximal clique for a given graph
 * @param input_char  an encoded string containing the graph
 * @param length      the number of couple of vertices in the graph having a common edge
 * @param output_char the string in which the encoded result will be stored
 */
void color_reducer(char* input_char, uint32_t length, char* output_char) {
  bool **conn;
  int size;
  read_colors(input_char, length, conn, size);

  Maxclique m(conn, size);
  int *qmax;
  int qsize;
  m.mcq(qmax, qsize);
  for (int i = 0; i < qsize; i++) {
      if ((qmax[i] & 0xFF00) == 0) {
          output_char[i * 4] = '\x01';
          output_char[i * 4 + 1] = '\x01';
      } else {
          output_char[i * 4] = '\x02';
          assert((qmax[i] >> 8) != 0);
          output_char[i * 4 + 1] = char(qmax[i] >> 8);
      }

      if ((qmax[i] & 0x00FF) == 0) {
          output_char[i * 4 + 2] = '\x01';
          output_char[i * 4 + 3] = '\x01';
      } else {
          output_char[i * 4 + 2] = '\x02';
          assert((qmax[i] & 0x00FF) != 0);
          output_char[i * 4 + 3] = char(qmax[i] & 0x00FF);
      }
  }
  delete [] qmax;
}
