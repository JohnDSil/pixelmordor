# mordor_prompt.sh - Prompt oficial temático de la Tierra de Mordor para Bash
# Activación: source ~/.config/pixelzen/mordor_prompt.sh (o con 'mordor prompt on')

__mordor_git_branch() {
    local b dirty
    if b=$(git symbolic-ref --short HEAD 2>/dev/null); then
        if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
            echo -e " \033[1;31m(${b} 🌋)\033[0m"
        else
            echo -e " \033[1;33m(${b} 💍)\033[0m"
        fi
    fi
}

__mordor_prompt_command() {
    local exit_code=$?
    local arrow_col="\[\033[1;33m\]" # Dorado si exit == 0
    if [ $exit_code -ne 0 ]; then
        arrow_col="\[\033[1;31m\]" # Rojo sangre si error
    fi
    local git_status
    git_status=$(__mordor_git_branch)
    PS1="\[\033[1;31m\]👁 [\[\033[1;37m\]\u\[\033[1;31m\]@\[\033[1;33m\]\h\[\033[1;31m\]:\[\033[1;34m\]\w\[\033[1;31m\]]${git_status} ${arrow_col}❯\[\033[0m\] "
}

PROMPT_COMMAND="__mordor_prompt_command"
