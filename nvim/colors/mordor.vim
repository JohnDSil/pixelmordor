" ====================================================================
" Mordor.vim - Esquema de colores para Vim & Neovim
" La Tierra de las Sombras (El Señor de los Anillos)
" ====================================================================

set background=dark
hi clear
if exists("syntax_on")
  syntax reset
endif
let g:colors_name = "mordor"

" Paleta de Colores GUI & 256
" Fondo: #0d0308 | Texto: #e6dedc | Rojo: #ef4444 | Oro: #f59e0b | Ceniza: #6b7280

hi Normal          guifg=#e6dedc guibg=#0d0308 ctermfg=254 ctermbg=232
hi NonText         guifg=#4a1525 guibg=#0d0308 ctermfg=238 ctermbg=232
hi CursorLine      guibg=#1a0612 ctermbg=234   gui=none cterm=none
hi CursorColumn    guibg=#1a0612 ctermbg=234
hi LineNr          guifg=#5c1d2e guibg=#0d0308 ctermfg=238
hi CursorLineNr    guifg=#f59e0b guibg=#1a0612 ctermfg=214 gui=bold cterm=bold

hi Comment         guifg=#6b7280 ctermfg=244   gui=italic cterm=italic
hi Constant        guifg=#f97316 ctermfg=208
hi String          guifg=#f59e0b ctermfg=214
hi Character       guifg=#f59e0b ctermfg=214
hi Number          guifg=#f97316 ctermfg=208
hi Boolean         guifg=#dc2626 ctermfg=160   gui=bold cterm=bold
hi Float           guifg=#f97316 ctermfg=208

hi Identifier      guifg=#fca5a5 ctermfg=217
hi Function        guifg=#ef4444 ctermfg=196   gui=bold cterm=bold

hi Statement       guifg=#dc2626 ctermfg=160   gui=bold cterm=bold
hi Conditional     guifg=#ef4444 ctermfg=196   gui=bold cterm=bold
hi Repeat          guifg=#ef4444 ctermfg=196   gui=bold cterm=bold
hi Label           guifg=#f59e0b ctermfg=214
hi Operator        guifg=#f87171 ctermfg=203
hi Keyword         guifg=#ef4444 ctermfg=196   gui=bold cterm=bold
hi Exception       guifg=#dc2626 ctermfg=160   gui=bold cterm=bold

hi PreProc         guifg=#f97316 ctermfg=208
hi Include         guifg=#f97316 ctermfg=208
hi Define          guifg=#f97316 ctermfg=208
hi Macro           guifg=#f59e0b ctermfg=214
hi PreCondit       guifg=#f97316 ctermfg=208

hi Type            guifg=#fbbf24 ctermfg=214   gui=bold cterm=bold
hi StorageClass    guifg=#ef4444 ctermfg=196
hi Structure       guifg=#fbbf24 ctermfg=214
hi Typedef         guifg=#fbbf24 ctermfg=214

hi Special         guifg=#dc2626 ctermfg=160
hi SpecialChar     guifg=#f59e0b ctermfg=214
hi Tag             guifg=#ef4444 ctermfg=196
hi Delimiter       guifg=#e6dedc ctermfg=254
hi SpecialComment  guifg=#8a3440 ctermfg=95
hi Debug           guifg=#f97316 ctermfg=208

hi Underlined      guifg=#f59e0b gui=underline cterm=underline
hi Ignore          guifg=#4a1525 ctermfg=238
hi Error           guifg=#ffffff guibg=#dc2626 ctermfg=15 ctermbg=160 gui=bold cterm=bold
hi Todo            guifg=#0d0308 guibg=#f59e0b ctermfg=232 ctermbg=214 gui=bold cterm=bold

hi Visual          guifg=#ffffff guibg=#7f1d1d ctermfg=15 ctermbg=88
hi Search          guifg=#0d0308 guibg=#f59e0b ctermfg=232 ctermbg=214 gui=bold cterm=bold
hi IncSearch       guifg=#0d0308 guibg=#ef4444 ctermfg=232 ctermbg=196 gui=bold cterm=bold

hi StatusLine      guifg=#fef08a guibg=#260a16 ctermfg=228 ctermbg=234 gui=bold cterm=bold
hi StatusLineNC    guifg=#6b7280 guibg=#14050d ctermfg=244 ctermbg=233
hi VertSplit       guifg=#4a1525 guibg=#0d0308 ctermfg=238 ctermbg=232
hi Pmenu           guifg=#e6dedc guibg=#1a0612 ctermfg=254 ctermbg=234
hi PmenuSel        guifg=#ffffff guibg=#991b1b ctermfg=15 ctermbg=88 gui=bold cterm=bold
hi PmenuSbar       guibg=#12040b ctermbg=233
hi PmenuThumb      guibg=#dc2626 ctermbg=160
