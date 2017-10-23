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

if [[ "$1" -eq "-h" ]]; then
	echo "usage: bash export_gnome.sh <Profile Name> <path/to/tmp/file> [<path/to/terminal/profiles> | ]"
	exit 0
fi

# first argument is profile name
PROFILE_NAME=$1; shift
# second argument is tmp file with colors
i=1
while IFS='' read -r line || [[ -n "$line" ]]; do
	declare "COLOR_$i=$(gnome_color \"$line\")"
	((i++))
done < "$1"
# first before last one is background
BACKGROUND_COLOR=$COLOR_17
# last is foreground
FOREGROUND_COLOR=$COLOR_18

shift; BASE_KEY_NEW=$1
[[ -z "$BASE_KEY_NEW" ]] && BASE_KEY_NEW=/org/gnome/terminal/legacy/profiles:

[[ -z "$PROFILE_NAME" ]] && PROFILE_NAME="Default"
[[ -z "$PROFILE_SLUG" ]] && PROFILE_SLUG="Default"
[[ -z "$DCONF" ]] && DCONF=dconf
[[ -z "$UUIDGEN" ]] && UUIDGEN=uuidgen

# Newest versions of gnome-terminal use dconf
if which "$DCONF" > /dev/null 2>&1; then

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

    # because list is empty after reset
	if [[ ! -n "`$DCONF list $BASE_KEY_NEW/`" ]]; then
        dset use-theme-colors "true"
        dset use-theme-colors "false"
    fi

    if [[ -n "'$DCONF list $BASE_KEY_NEW/'" ]]; then
		# copy existing settings from default profile
		$DCONF dump "$DEFAULT_KEY/" | $DCONF load "$PROFILE_KEY/"

		# add new copy to list of profiles
		dlist_append $BASE_KEY_NEW/list "$PROFILE_SLUG"

		# update profile values with theme options
		set_theme
		dset palette "['${COLOR_01}', '${COLOR_02}', '${COLOR_03}', '${COLOR_04}', '${COLOR_05}', '${COLOR_06}', '${COLOR_07}', '${COLOR_08}', '${COLOR_09}', '${COLOR_10}', '${COLOR_11}', '${COLOR_12}', '${COLOR_13}', '${COLOR_14}', '${COLOR_15}', '${COLOR_16}']"

        unset PROFILE_NAME
		unset PROFILE_SLUG
        unset PROFILE_KEY
        unset DEFAULT_KEY
        unset BASE_KEY_NEW
		unset DCONF
		unset UUIDGEN
		exit 0
	fi
fi
