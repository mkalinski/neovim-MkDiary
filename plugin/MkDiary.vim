" Copyright 2022 Michał Kaliński

if get(g:, 'loaded_MkDiary', 0)
    finish
endif

let g:loaded_MkDiary = 1

command -nargs=* -bang -bar MkDiary call MkDiary_open(get(g:, 'MkDiary_edit_command', 'edit') .. <q-bang>, <q-args>)
command -nargs=* -bar MkDiarySplit call MkDiary_open(<q-mods> .. ' ' .. get(g:, 'MkDiary_split_command', 'split'), <q-args>)
