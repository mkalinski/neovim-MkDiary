do -- assert sane difftime
    local t1 = os.time{year = 2000, month = 10, day = 10}
    local t2 = os.time{year = 2000, month = 10, day = 11}

    assert(
        os.difftime(t2, t1) == t2 - t1,
        "mkdiary: This system's os.time does not return value in seconds. "
        .. "MkDiary can't function on this system."
    )
end

local M = {}

local DAY_IN_SECONDS = 24 * 60 * 60

local settings = {
    base_dir = vim.fs.normalize'~/Diary',
    file_ext = '.txt'
}

local function error_invalid_args(entry_elements)
    error('mkdiary: Invalid path elements: ' .. vim.inspect(entry_elements))
end

local function lazy_now()
    local now

    return function()
        if not now then
            now = os.date'*t'
        end

        return now
    end
end

local function fold_date_args_to_table(fold_func)
    -- The order matches args to MkDiary commands.
    return vim.iter(ipairs{'year', 'month', 'day'}):fold({}, fold_func)
end

local function get_relative_days_date(days_d)
    return os.date('*t', os.time() + days_d * DAY_IN_SECONDS)
end

local function try_parse_relative_days(arg)
    local sign, number = string.match(arg, '^([+-])(%d+)d?$')

    if not sign then
        return nil
    end

    if sign == '-' then
        return -number
    end

    return tonumber(number)
end

local function parse_absolute_date(args)
    local ln = lazy_now()

    return fold_date_args_to_table(function(acc, idx, key)
        local arg = args[idx]

        if arg then
            if arg == '.' then
                acc[key] = ln()[key]
            else
                local abs_number = tonumber(arg)

                if not abs_number or abs_number < 1 then
                    error_invalid_args(args)
                end

                acc[key] = abs_number
            end
        end

        return acc
    end)
end

local function open_entry(open_command, entry_elements)
    local normalized_elements = fold_date_args_to_table(function(acc, _, key)
        if entry_elements[key] then
            acc[key] = string.format('%02u', entry_elements[key])
        end

        return acc
    end)

    if normalized_elements.year then
        -- If there is at least one valid entry element,
        -- we can create the year or month directory.
        local entry_dir = vim.fs.joinpath(
            settings.base_dir,
            normalized_elements.year,
            normalized_elements.month
        )
        vim.fn.mkdir(entry_dir, 'p')

        -- If the third and final entry element is present,
        -- open the full entry filename, else open the entry directory.
        local entry

        if normalized_elements.day then
            entry = vim.fs.joinpath(
                entry_dir,
                normalized_elements.day .. settings.file_ext
            )
        else
            entry = entry_dir
        end

        vim.cmd(open_command .. ' ' .. vim.fn.fnameescape(entry))
        vim.cmd.lcd(settings.base_dir)
    else
        error_invalid_args(entry_elements)
    end
end

local function handle_args(open_command, args)
    local nargs = #args

    if nargs == 0 then
        open_entry(open_command, os.date'*t')
        return
    end

    if nargs == 1 then
        local relative_days = try_parse_relative_days(args[1])

        if relative_days then
            open_entry(open_command, get_relative_days_date(relative_days))
            return
        end
    end

    open_entry(open_command, parse_absolute_date(args))
end

function M.setup(opts)
    settings = vim.tbl_extend("force", settings, opts)

    vim.api.nvim_create_user_command('MkDiary',
        function(ctx)
            local open_command = 'edit'

            if ctx.bang then
                open_command = open_command .. '!'
            end

            handle_args(open_command, ctx.fargs)
        end,
        {
            desc = 'Open diary entry in the current window.',
            nargs = '*',
            bang = true,
            bar = true
        }
    )

    vim.api.nvim_create_user_command('MkDiarySplit',
        function(ctx)
            handle_args(ctx.mods .. ' split', ctx.fargs)
        end,
        {
            desc = 'Open diary entry in a split window.',
            nargs = '*',
            bar = true
        }
    )
end

return M
