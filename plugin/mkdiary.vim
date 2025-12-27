" Copyright 2025 mkalinski

if get(g:, 'loaded_mkdiary', 0)
    finish
endif

let g:loaded_mkdiary = 1

if !has('python3')
    echoerr 'mkdiary: Python 3 is required, but not provided'
    finish
endif

command -nargs=* -bang -bar MkDiary call mkdiary#open(<q-bang>, <f-args>)
command -nargs=* -bar MkDiarySplit call mkdiary#split(<q-mods>, <f-args>)
