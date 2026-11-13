-- Mordor colorscheme for Neovim (Lua)
-- Tierra de las Sombras (El Señor de los Anillos)

local M = {}

M.colors = {
  bg         = "#0d0308",
  fg         = "#e6dedc",
  cursorline = "#1a0612",
  comment    = "#6b7280",
  keyword    = "#ef4444",
  constant   = "#f97316",
  string     = "#f59e0b",
  func       = "#ef4444",
  type       = "#fbbf24",
  visual     = "#7f1d1d",
  error      = "#dc2626",
  warning    = "#f59e0b",
  border     = "#782622",
}

function M.setup()
  vim.cmd("hi clear")
  if vim.fn.exists("syntax_on") == 1 then
    vim.cmd("syntax reset")
  end
  vim.o.background = "dark"
  vim.g.colors_name = "mordor"

  local hl = function(group, opts)
    vim.api.nvim_set_hl(0, group, opts)
  end

  local c = M.colors
  hl("Normal",       { fg = c.fg, bg = c.bg })
  hl("Comment",      { fg = c.comment, italic = true })
  hl("Constant",     { fg = c.constant })
  hl("String",       { fg = c.string })
  hl("Function",     { fg = c.func, bold = true })
  hl("Keyword",      { fg = c.keyword, bold = true })
  hl("Statement",    { fg = c.keyword, bold = true })
  hl("Type",         { fg = c.type, bold = true })
  hl("Visual",       { bg = c.visual, fg = "#ffffff" })
  hl("CursorLine",   { bg = c.cursorline })
  hl("LineNr",       { fg = "#5c1d2e" })
  hl("CursorLineNr", { fg = c.string, bold = true })
  hl("StatusLine",   { bg = "#260a16", fg = "#fef08a", bold = true })
  hl("Pmenu",        { bg = c.cursorline, fg = c.fg })
  hl("PmenuSel",     { bg = "#991b1b", fg = "#ffffff", bold = true })
end

return M
