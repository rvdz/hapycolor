:function! Get()
:    redir @a | set rtp | redir END
:    let a = writefile([@a], "plugin_paths.txt")
:    quit
:endfunction
:call Get()
