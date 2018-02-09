:function! GetPlugins(cmd)
:  redir => message
:  silent execute a:cmd
:  redir END
:  setlocal bufhidden=wipe noswapfile nobuflisted nomodified
:  silent put=message
:endfunction
:command! -nargs=+ -complete=command GetPlugins call GetPlugins(<q-args>)
:GetPlugins scriptnames
:wq
