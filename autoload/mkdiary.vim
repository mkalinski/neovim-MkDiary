" Copyright 2025 mkalinski

if !has('python3')
    echoerr 'mkdiary: Python 3 is required, but not provided'
    finish
endif

python3 << EOF
# Because it's an autoload file, this is guaranteed to be executed once.
# Initialize in a function to avoid polluting global namespace.
# Python is still required, because it has timedelta by days.
def _mkdiary_setup():
    import datetime
    import functools

    class MkDiaryDateHandler:
        @functools.cached_property
        def _today(self):
            return datetime.date.today()

        def handle_absolute_date(self, year, month, day):
            year = self._today.year if year == '.' else int(year)

            if month:
                month = self._today.month if month == '.' else int(month)

            if day:
                day = self._today.day if day == '.' else int(day)

            return [year, month, day]

        def handle_relative_date(self, relative_days):
            target_date = self._today + datetime.timedelta(days=relative_days)

            return [target_date.year, target_date.month, target_date.day]

    return MkDiaryDateHandler

MkDiaryDateHandler = _mkdiary_setup()
del _mkdiary_setup
EOF

function s:get_base_dir() abort
    return exists('g:MkDiary_base_dir')
    \   ? g:MkDiary_base_dir
    \   : $HOME .. '/Diary'
endfunction

function s:get_file_ext() abort
    return exists('g:MkDiary_file_ext') ? g:MkDiary_file_ext : '.txt'
endfunction

function s:open_entry(open_command, elements) abort
    let l:base_dir = trim(s:get_base_dir(), '/', 2) .. '/'
    let l:fmt_elts = s:prepare_entry_elements(a:elements)

    if len(l:fmt_elts) >= 1
        " If there is at least one valid entry element,
        " we can create the year or month directory.
        let l:entry_dir = l:base_dir .. join(l:fmt_elts[0:1], '/')
        call mkdir(l:entry_dir, 'p')

        " If the third and final entry element is present,
        " open the full entry filename, else open the entry directory.
        let l:entry = len(l:fmt_elts) >= 3
        \   ? l:entry_dir .. '/' .. l:fmt_elts[2] .. s:get_file_ext()
        \   : l:entry_dir

        exe a:open_command fnameescape(l:entry)
        call chdir(l:base_dir)
    else
        throw 'mkdiary: Invalid path elements list: ' .. a:elements
    endif
endfunction

function s:prepare_entry_elements(elements) abort
    let l:result = []

    for l:elt in a:elements
        let l:fmt_elt = printf('%02u', l:elt)

        " This will be formatted into 00 on any sort of invalid value.
        " Stop formatting at the first invalid value,
        " to only pass valid combinations.
        if l:fmt_elt ==# '00'
            break
        endif

        call add(l:result, l:fmt_elt)
    endfor

    return l:result
endfunction

function s:open_absolute_entry(open_command, year, month, day) abort
    let l:pyexpr = printf(
    \   'MkDiaryDateHandler().handle_absolute_date("%s", "%s", "%s")',
    \   escape(a:year, '"\'),
    \   escape(a:month, '"\'),
    \   escape(a:day, '"\')
    \)
    let l:entry_elements = py3eval(l:pyexpr)
    call s:open_entry(a:open_command, l:entry_elements)
endfunction

function s:open_relative_entry(open_command, relative_days) abort
    let l:pyexpr = printf(
    \   'MkDiaryDateHandler().handle_relative_date(%d)',
    \   a:relative_days
    \)
    let l:entry_elements = py3eval(l:pyexpr)
    call s:open_entry(a:open_command, l:entry_elements)
endfunction

function s:try_parse_relative_days(arg) abort
    let l:match = matchlist(a:arg, '^\([+-]\)\(\d\+\)d\?$')

    if empty(l:match)
        return 0
    endif

    let [l:sign, l:number] = l:match[1:2]

    if l:sign ==# '-'
        let l:number = -l:number
    endif

    return +l:number
endfunction

function s:handle_args(open_command, args) abort
    let l:args_len = len(a:args)

    if l:args_len == 0
        call s:open_absolute_entry(a:open_command, '.', '.', '.')
        return
    endif

    if l:args_len == 1
        let l:relative_days = s:try_parse_relative_days(a:args[0])

        if l:relative_days
            call s:open_relative_entry(a:open_command, l:relative_days)
            return
        endif
    endif

    call s:open_absolute_entry(
    \   a:open_command,
    \   a:args[0],
    \   l:args_len > 1 ? a:args[1] : '',
    \   l:args_len > 2 ? a:args[2] : ''
    \)
endfunction

function mkdiary#open(bang, ...) abort
    call s:handle_args('edit' .. a:bang, a:000)
endfunction

function mkdiary#split(mods, ...) abort
    call s:handle_args(trim(a:mods .. ' split'), a:000)
endfunction
