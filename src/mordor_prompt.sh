# mordor_prompt.sh - Prompt oficial temático de la Tierra de Mordor para Bash
# Activación: source ~/.config/pixelzen/mordor_prompt.sh (o con 'mordor prompt on')

__mordor_git_branch() {
    local b
    b=$(git branch --show-current 2>/dev/null)
    if [ -z "$b" ]; then
        b=$(git rev-parse --short HEAD 2>/dev/null)
    fi
    if [ -n "$b" ]; then
        if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
            echo " \[\033[1;31m\](${b} 🌋)\[\033[0m\]"
        else
            echo " \[\033[1;33m\](${b} 💍)\[\033[0m\]"
        fi
    fi
}

__mordor_play_sound() {
    local snd="$1"
    local f="$HOME/.local/share/gnome-shell/extensions/pixelzen@mosqui1988.github.io/sounds/${snd}.wav"
    [ -f "$f" ] || f="$HOME/.local/share/pixelzen/sounds/${snd}.wav"
    if [ -f "$f" ]; then
        ( (canberra-gtk-play -f "$f" >/dev/null 2>&1 || pw-play "$f" >/dev/null 2>&1 || aplay -q "$f" >/dev/null 2>&1 || true) & ) 2>/dev/null
    fi
}

__mordor_prompt_command() {
    local exit_code=$?
    if [ -f "$HOME/.config/pixelzen/campana_activa" ] && [ $exit_code -ne 0 ]; then
        __mordor_play_sound sauron
    fi
    local arrow_col="\[\033[1;33m\]" # Dorado si exit == 0
    if [ $exit_code -ne 0 ]; then
        arrow_col="\[\033[1;31m\]"   # Rojo sangre si error
    fi
    local git_status
    git_status=$(__mordor_git_branch)
    PS1="\[\033[1;31m\]👁 [\[\033[1;37m\]\u\[\033[1;31m\]@\[\033[1;33m\]\h\[\033[1;31m\]:\[\033[1;34m\]\w\[\033[1;31m\]]${git_status} ${arrow_col}❯\[\033[0m\] "
}

if [[ "$(declare -p PROMPT_COMMAND 2>/dev/null)" =~ "declare -a" ]]; then
    # Bash 5.1+ con array en PROMPT_COMMAND
    if [[ ! " ${PROMPT_COMMAND[*]} " =~ " __mordor_prompt_command " ]]; then
        PROMPT_COMMAND+=(__mordor_prompt_command)
    fi
else
    if [[ ! "${PROMPT_COMMAND:-}" =~ "__mordor_prompt_command" ]]; then
        PROMPT_COMMAND="__mordor_prompt_command; ${PROMPT_COMMAND:-:}"
    fi
fi

# Aplicar inmediatamente en la sesión actual
__mordor_prompt_command
