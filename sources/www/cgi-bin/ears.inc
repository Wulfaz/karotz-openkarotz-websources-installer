#!/bin/bash

usedbus=0
uuid_ears=$(uuidgen)

function EarsReset {
	dbus-send --system --type=method_call --dest=com.mindscape.karotz.Ears /com/mindscape/karotz/Ears \
		com.mindscape.karotz.KarotzInterface.reset string:${uuid_ears} string:1
}

function EarMoveRight {
	dbus-send --system --type=method_call --dest=com.mindscape.karotz.Ears /com/mindscape/karotz/Ears \
		com.mindscape.karotz.KarotzInterface.move_right string:${uuid_ears} string:1 string:3
}

function EarsMove {
	dbus-send --system --type=method_call --dest=com.mindscape.karotz.Ears /com/mindscape/karotz/Ears \
		com.mindscape.karotz.KarotzInterface.move string:${uuid_ears} int32:$1 int32:$3 int32:$2 int32:$3

}

function dbus_EarsStep {
	dbus-send --system --type=method_call --dest=com.mindscape.karotz.Ears /com/mindscape/karotz/Ears \
		com.mindscape.karotz.KarotzInterface.move string:${uuid_ears} int32:$1 int32:$3 int32:$2 int32:$3
}

function CheckEarsNotDisabled {
	if [ -e "${CNF_DATADIR}/Run/ears.disabled" ]; then
		DATA='{"return":"1","msg":"Unable to perform action, ears are disabled."}'
		Log "[Ears]" "Unable to perform action, ears are disabled." 1
		SendResponse "${DATA}"
		exit 0
	fi
}
