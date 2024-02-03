autocmd VimEnter * redraw!
let timestamp = argv(0)
silent
execute 'cd ~/data'
execute 'edit' g:timestamp . '.dat'
set splitright
execute 'vsplit' g:timestamp . '-bankacctb.dat'
execute 'split' g:timestamp . '-bankaccta.dat'
redraw
