#!/bin/bash

declare -A URLParam

# ---------------------------------------------------------------------------
#
# ---------------------------------------------------------------------------
function ReadUrlParams {
	saveIFS=${IFS}
	IFS='=&'
	parm=${QUERY_STRING}
	IFS=${saveIFS}
	for ((i = 0; i < ${#parm[@]}; i += 2)); do
		URLParam[${parm[i]}]=${parm[i + 1]}
	done
}

# ---------------------------------------------------------------------------
#
# ---------------------------------------------------------------------------
function UrlDecode {
	echo -e "$(sed 's/+/ /g; s/%/\\x/g')"
}

# ---------------------------------------------------------------------------
#
# ---------------------------------------------------------------------------
function UrlEncode() {
	local string="$1"
	local strlen=${#string}
	local encoded=""
	for ((pos = 0; pos < strlen; pos++)); do
		c=${string:pos:1}
		case "${c}" in
			[-_.~a-zA-Z0-9]) o="${c}" ;;
			*) printf -v o '%%%02x' "'${c}" ;;
		esac
		encoded+="${o}"
	done
	echo "${encoded}"
}
