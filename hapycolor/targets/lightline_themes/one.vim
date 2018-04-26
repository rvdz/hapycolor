let s:grey1  = [ '#5c6370', 59 ]
let s:grey2  = [ '#2c323d', 237 ]
let s:grey3  = [ '#3e4452', 59 ]

let s:p = {'normal': {}, 'inactive': {}, 'insert': {}, 'replace': {}, 'visual': {}, 'tabline': {}}
let s:p.normal.left     = [ [ s:background, s:blue, 'bold' ], [ s:foreground, s:grey3 ] ]
let s:p.normal.middle   = [ [ s:foreground, s:grey2 ] ]
let s:p.normal.right   = [ [ s:background, s:blue, 'bold' ], [ s:background, s:blue, 'bold' ] ]
let s:p.normal.error   = [ [ s:red,   s:background ] ]
let s:p.normal.warning = [ [ s:yellow, s:background ] ]

let s:p.inactive.left   = [ [ s:grey1,  s:background ], [ s:grey1, s:background ] ]
let s:p.inactive.middle = [ [ s:grey1, s:grey2 ] ]
let s:p.inactive.right  = [ [ s:grey1, s:background ], [ s:grey1, s:background ] ]

let s:p.insert.left     = [ [ s:background, s:green, 'bold' ], [ s:foreground, s:grey3 ] ]
let s:p.insert.right   = [ [ s:background, s:green, 'bold' ], [ s:background, s:green, 'bold' ] ]

let s:p.replace.left    = [ [ s:background, s:red, 'bold' ], [ s:foreground, s:grey3 ] ]
let s:p.replace.right  = [ [ s:background, s:red, 'bold' ], [ s:background, s:red, 'bold' ] ]

let s:p.visual.left     = [ [ s:background, s:magenta, 'bold' ], [ s:foreground, s:grey3 ] ]
let s:p.visual.right   = [ [ s:background, s:magenta, 'bold' ], [ s:background, s:magenta, 'bold' ] ]

let s:p.tabline.left   = [ [ s:background, s:grey3 ] ]
let s:p.tabline.middle = [ [ s:grey3, s:grey2 ] ]
let s:p.tabline.right  = copy(s:p.normal.right)
let s:p.tabline.tabsel = [ [ s:background, s:magenta, 'bold' ] ]
