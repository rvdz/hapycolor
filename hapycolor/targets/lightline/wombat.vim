let s:grey03 = [ '#242424', 235 ]
let s:grey023 = [ '#353535 ', 236 ]
let s:grey02 = [ '#444444 ', 238 ]
let s:grey01 = [ '#585858', 240 ]
let s:grey00 = [ '#666666', 242  ]
let s:grey0 = [ '#808080', 244 ]
let s:grey1 = [ '#969696', 247 ]
let s:grey2 = [ '#a8a8a8', 248 ]
let s:grey3 = [ '#d0d0d0', 252 ]

let s:yellow = [ '#d3bb06', 204 ]
let s:red = [ '#d35506', 190 ]

let s:normal = [ $NORMAL ]
let s:insert = [ $INSERT ]
let s:visual = [ $VISUAL ]
let s:replace = [ $REPLACE ]

let s:p = {'normal': {}, 'inactive': {}, 'insert': {}, 'replace': {}, 'visual': {}, 'tabline': {}}
let s:p.normal.left = [ [ s:grey02, s:normal ], [ s:grey3, s:grey01 ] ]
let s:p.normal.right = [ [ s:grey02, s:grey0 ], [ s:grey1, s:grey01 ] ]
let s:p.inactive.right = [ [ s:grey023, s:grey01 ], [ s:grey00, s:grey02 ] ]
let s:p.inactive.left =  [ [ s:grey1, s:grey02 ], [ s:grey00, s:grey023 ] ]
let s:p.insert.left = [ [ s:grey02, s:insert ], [ s:grey3, s:grey01 ] ]
let s:p.replace.left = [ [ s:grey023, s:replace ], [ s:grey3, s:grey01 ] ]
let s:p.visual.left = [ [ s:grey02, s:visual ], [ s:grey3, s:grey01 ] ]
let s:p.normal.middle = [ [ s:grey2, s:grey02 ] ]
let s:p.inactive.middle = [ [ s:grey1, s:grey023 ] ]
let s:p.tabline.left = [ [ s:grey3, s:grey00 ] ]
let s:p.tabline.tabsel = [ [ s:grey3, s:grey03 ] ]
let s:p.tabline.middle = [ [ s:grey2, s:grey02 ] ]
let s:p.tabline.right = [ [ s:grey2, s:grey00 ] ]
let s:p.normal.error = [ [ s:grey03, s:red ] ]
let s:p.normal.warning = [ [ s:grey023, s:yellow ] ]

let g:lightline#colorscheme#hapycolor#palette = lightline#colorscheme#flatten(s:p)"
