let s:cuicolors = {
      \ 'base03': [ '8', '234', 'DarkGray' ],
      \ 'base02': [ '0', '235', 'Black' ],
      \ 'base01': [ '10', '239', 'LightGreen' ],
      \ 'base00': [ '11', '240', 'LightYellow' ],
      \ 'base0':  [ '12', '244', 'LightBlue' ],
      \ 'base1':  [ '14', '245', 'LightCyan' ],
      \ 'base2': [ '7', '187', 'LightGray' ],
      \ 'base3': [ '15', '230', 'White' ],
      \ }

" The following condition only applies for the console and is the same
" condition vim-colors-solarized uses to determine which set of colors
" to use.
let s:solarized_termcolors = get(g:, 'solarized_termcolors', 256)
if s:solarized_termcolors != 256 && &t_Co >= 16
  let s:cuiindex = 0
elseif s:solarized_termcolors == 256
  let s:cuiindex = 1
else
  let s:cuiindex = 2
endif

let s:base03 = [ '#002b36', s:cuicolors.base03[s:cuiindex] ]
let s:base02 = [ '#073642', s:cuicolors.base02[s:cuiindex] ]
let s:base01 = [ '#586e75', s:cuicolors.base01[s:cuiindex] ]
let s:base00 = [ '#657b83', s:cuicolors.base00[s:cuiindex] ]
let s:base0 = [ '#839496', s:cuicolors.base0[s:cuiindex] ]
let s:base1 = [ '#93a1a1', s:cuicolors.base1[s:cuiindex] ]
let s:base2 = [ '#eee8d5', s:cuicolors.base2[s:cuiindex] ]
let s:base3 = [ '#fdf6e3', s:cuicolors.base3[s:cuiindex] ]

if &background ==# 'light'
  let [ s:base03, s:base3 ] = [ s:base3, s:base03 ]
  let [ s:base02, s:base2 ] = [ s:base2, s:base02 ]
  let [ s:base01, s:base1 ] = [ s:base1, s:base01 ]
  let [ s:base00, s:base0 ] = [ s:base0, s:base00 ]
endif

let s:normal = [ $NORMAL ]
let s:insert = [ $INSERT ]
let s:visual = [ $VISUAL ]
let s:replace = [ $REPLACE ]

let s:yellow = [ '#d3bb06', 204 ]
let s:red = [ '#d35506', 190 ]

let s:p = {'normal': {}, 'inactive': {}, 'insert': {}, 'replace': {}, 'visual': {}, 'tabline': {}}
let s:p.normal.left = [ [ s:base03, s:normal ], [ s:base03, s:base00 ] ]
let s:p.normal.right = [ [ s:base03, s:base1 ], [ s:base03, s:base00 ] ]
let s:p.inactive.right = [ [ s:base03, s:base00 ], [ s:base0, s:base02 ] ]
let s:p.inactive.left =  [ [ s:base0, s:base02 ], [ s:base0, s:base02 ] ]
let s:p.insert.left = [ [ s:base03, s:insert ], [ s:base03, s:base00 ] ]
let s:p.replace.left = [ [ s:base03, s:replace ], [ s:base03, s:base00 ] ]
let s:p.visual.left = [ [ s:base03, s:visual ], [ s:base03, s:base00 ] ]
let s:p.normal.middle = [ [ s:base1, s:base02 ] ]
let s:p.inactive.middle = [ [ s:base01, s:base02 ] ]
let s:p.tabline.left = [ [ s:base03, s:base00 ] ]
let s:p.tabline.tabsel = [ [ s:base03, s:base1 ] ]
let s:p.tabline.middle = [ [ s:base0, s:base02 ] ]
let s:p.tabline.right = copy(s:p.normal.right)
let s:p.normal.error = [ [ s:base03, s:red ] ]
let s:p.normal.warning = [ [ s:base03, s:yellow ] ]
