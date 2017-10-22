#! /bin/bash

### Convert RGB colors to Gnome colors
gnome_color () {

    AA=${1:1:2}
    BB=${1:3:2}
    CC=${1:5:2}

    echo "#${AA}${AA}${BB}${BB}${CC}${CC}"
}

### Write dconf key values
dset() {
    local key="$1"; shift
    local val="$1"; shift

    if [[ "$type" == "string" ]]; then
        val="'$val'"
    fi

    "$DCONF" write "$PROFILE_KEY/$key" "$val"
}


###
set_theme() {
    dset visible-name "'$PROFILE_NAME'"
    dset background-color "'${BACKGROUND_COLOR}'"
    dset foreground-color "'${FOREGROUND_COLOR}'"
    if [ ! -z "${BOLD_COLOR}" ]; then
        dset bold-color "'${BOLD_COLOR}'"
        dset bold-color-same-as-fg "false"
    else
        dset bold-color "'${COLOR_08}'"
        dset bold-color-same-as-fg "true"
    fi
    dset use-theme-colors "false"
    dset use-theme-background "false"
}


###
dlist_append() {
    local key="$1"; shift
    local val="$1"; shift

    local entries="$(
            {
                "$DCONF" read "$key" | tr -d '[]' | tr , "\n" | fgrep -v "$val"
                echo "'$val'"
            } | head -c-1 | tr "\n" ,
        )"

    "$DCONF" write "$key" "[$entries]"
}


##### TEST LINES
COLOR_01="#000000"           # HOST
COLOR_02="#e52222"           # SYNTAX_STRING
COLOR_03="#a6e32d"           # COMMAND
COLOR_04="#fc951e"           # COMMAND_COLOR2
COLOR_05="#c48dff"           # PATH
COLOR_06="#fa2573"           # SYNTAX_VAR
COLOR_07="#67d9f0"           # PROMP
COLOR_08="#f2f2f2"           #

COLOR_09="#555555"           #
COLOR_10="#ff5555"           # COMMAND_ERROR
COLOR_11="#55ff55"           # EXEC
COLOR_12="#ffff55"           #
COLOR_13="#5555ff"           # FOLDER
COLOR_14="#ff55ff"           #
COLOR_15="#55ffff"           #
COLOR_16="#ffffff"           #

BACKGROUND_COLOR="#000000"   # Background Color
FOREGROUND_COLOR="#555555"   # Text
CURSOR_COLOR="$FOREGROUND_COLOR" # Cursor
PROFILE_NAME="TEST"
##### END TEST

# |
# | Applying values on gnome-terminal
# | ===========================================
BACKGROUND_COLOR=$(gnome_color $BACKGROUND_COLOR)
FOREGROUND_COLOR=$(gnome_color $FOREGROUND_COLOR)
COLOR_01=$(gnome_color $COLOR_01)
COLOR_02=$(gnome_color $COLOR_02)
COLOR_03=$(gnome_color $COLOR_03)
COLOR_04=$(gnome_color $COLOR_04)
COLOR_05=$(gnome_color $COLOR_05)
COLOR_06=$(gnome_color $COLOR_06)
COLOR_07=$(gnome_color $COLOR_07)
COLOR_08=$(gnome_color $COLOR_08)
COLOR_09=$(gnome_color $COLOR_09)
COLOR_10=$(gnome_color $COLOR_10)
COLOR_11=$(gnome_color $COLOR_11)
COLOR_12=$(gnome_color $COLOR_12)
COLOR_13=$(gnome_color $COLOR_13)
COLOR_14=$(gnome_color $COLOR_14)
COLOR_15=$(gnome_color $COLOR_15)
COLOR_16=$(gnome_color $COLOR_16)


# |
# | Apply Variables
# | ===========================================

[[ -z "$PROFILE_NAME" ]] && PROFILE_NAME="Default"
[[ -z "$PROFILE_SLUG" ]] && PROFILE_SLUG="Default"
[[ -z "$DCONF" ]] && DCONF=dconf
[[ -z "$UUIDGEN" ]] && UUIDGEN=uuidgen

# Newest versions of gnome-terminal use dconf
if which "$DCONF" > /dev/null 2>&1; then
	[[ -z "$BASE_KEY_NEW" ]] && BASE_KEY_NEW=/org/gnome/terminal/legacy/profiles:

	if [[ -n "`$DCONF list $BASE_KEY_NEW/`" ]]; then
		if which "$UUIDGEN" > /dev/null 2>&1; then
			PROFILE_SLUG=`uuidgen`
		fi

		if [[ -n "`$DCONF read $BASE_KEY_NEW/default`" ]]; then
			DEFAULT_SLUG=`$DCONF read $BASE_KEY_NEW/default | tr -d \'`
		else
			DEFAULT_SLUG=`$DCONF list $BASE_KEY_NEW/ | grep '^:' | head -n1 | tr -d :/`
		fi

		DEFAULT_KEY="$BASE_KEY_NEW/:$DEFAULT_SLUG"
		PROFILE_KEY="$BASE_KEY_NEW/:$PROFILE_SLUG"

		# copy existing settings from default profile
		$DCONF dump "$DEFAULT_KEY/" | $DCONF load "$PROFILE_KEY/"

		# add new copy to list of profiles
		dlist_append $BASE_KEY_NEW/list "$PROFILE_SLUG"

		# update profile values with theme options
		set_theme
		dset palette "['${COLOR_01}', '${COLOR_02}', '${COLOR_03}', '${COLOR_04}', '${COLOR_05}', '${COLOR_06}', '${COLOR_07}', '${COLOR_08}', '${COLOR_09}', '${COLOR_10}', '${COLOR_11}', '${COLOR_12}', '${COLOR_13}', '${COLOR_14}', '${COLOR_15}', '${COLOR_16}']"

        unset PROFILE_NAME
		unset PROFILE_SLUG
		unset DCONF
		unset UUIDGEN
		exit 0
	fi
fi
