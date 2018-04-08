" Usage:
"   vim -s syntax_groups.vim
"
" This script generates an output file "./frequencies.py" which defines a
" dictionnary, linking each syntaxic group to its frequency.
" To do so, it requires a file named "./input_files.txt", located in the
" current directory, listing the paths of files for which vim is able perform
" a syntaxic analisis.
:function! Frequencies()
:    let filenames = readfile("input_files.txt")
:    let dic_string = ['syntax_group_frequencies = {']
:    let frequencies = {}
:    for f in filenames
:        execute 'edit' f
:        for l in range(line('$'))
:            for c in range(col('$'))
:                let group = synIDattr(synIDtrans(synID(l+1, c+1, 1)), 'name')
:                if has_key(frequencies, group)
:                    let frequencies[group] += 1
:                else
:                    let frequencies[group] = 1
:                endif
:            endfor
:        endfor
:    endfor
:    for [key, value] in items(frequencies)
:        let dic_string += ['"' . key . '" : ' . value . ',']
:    endfor
:    let dic_string += ['}']
:    let a =  writefile(dic_string, "frequencies.py")
:    quit
:endfunction
:call Frequencies()
