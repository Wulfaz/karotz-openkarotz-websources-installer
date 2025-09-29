#!/bin/bash

# ---------------------------------------------------------------------------
# Log message or error message
# ---------------------------------------------------------------------------
function Log {
	TAG=$1
	MSG=$2
	IS_ERR=$3
	if [ ${IS_ERR} -eq 1 ]; then
		logger -s "[OpenKarotz] [ERROR] ${TAG} ${MSG}" &>/dev/null
	else
		logger "[OpenKarotz] ${TAG} ${MSG}" &>/dev/null
	fi
}

# ---------------------------------------------------------------------------
# Check Karotz is not sleeping
# ---------------------------------------------------------------------------
function CheckIsNotSleeping {
	if [ -e "${CNF_DATADIR}/Run/karotz.sleep" ]; then
		DATA='{"return":"1","msg":"Unable to perform action, Karotz is sleeping."}'
		Log "[API]" "Karotz if sleeping." 1
		SendResponse "${DATA}"
		exit 0
	fi
}

# ---------------------------------------------------------------------------
# Check existing value for mandatory parameter
# ---------------------------------------------------------------------------
function CheckMandatoryParameter {
	VAL=$1
	NAME=$2
	if [ -z "${VAL}" ]; then
		Log "[API]" "Missing mandatory parameter: ('${NAME}')" 1
		DATA='{"return":"1","msg":"Missing mandatory parameter: ('${NAME}')."}'
		SendResponse "${DATA}"
		exit 0
	fi
}

# ---------------------------------------------------------------------------
# Check existing mandatory directory, create it if not
# ---------------------------------------------------------------------------
function CheckMandatoryDirectory {
	DIR_NAME=$1
	if [ ! -d "${DIR_NAME}" ]; then
		mkdir "${DIR_NAME}" &>/dev/null
		if [ ! -d "${DIR_NAME}" ]; then
			Log "[API]" "Missing directory: ('${DIR_NAME}')" 1
			DATA='{"return":"1","msg":"Missing '${DIR_NAME}' directory."}'
			SendResponse "${DATA}"
			exit 0
		fi
	fi
}

# ---------------------------------------------------------------------------
# Download folder content based on its list.txt file
# ---------------------------------------------------------------------------
function Download {
	URL=$1
	RDIR=$2
	LDIR=$3
	NAME=$4
	GROUP=$5
	NL=$6
	wget ${URL}${RDIR}/list.txt -O ${LDIR}/list.txt -q
	nbline=$(cat ${LDIR}/list.txt | wc -l)
	echo "----------------------------------------"
	echo "   Updating: "${NAME}
	echo "   ${nbline} File(s) to download"
	echo "----------------------------------------"
	i=1
	while read -r line; do
		n=$((i % GROUP))
		if [ ${n} -eq 0 ]; then
			echo -n "."
		fi
		wget ${URL}${RDIR}/${line} -q -O ${LDIR}/${line}
		chmod 644 ${LDIR}/${line}
		i=$((i + 1))
	done <${LDIR}/list.txt
	rm -f ${LDIR}/list.txt &>/dev/null
	echo ""
}

# ---------------------------------------------------------------------------
# Kill processes
# ---------------------------------------------------------------------------
function KillProcess {
	#  PROCESS=$1: Process to kill - CROND, SOUNDS, EARS, LED or "" for LED+EARS+SOUNDS (but not CROND!)
	case $1 in
		"LED")
			Log "[System]" "Stopping led process"
			/bin/killall led &>/dev/null
			;;
		"EARS")
			Log "[System]" "Stopping ears process"
			/bin/killall ears &>/dev/null
			;;
		"SOUDS")
			Log "[System]" "Stopping sounds process"
			/bin/killall madplay &>/dev/null
			/bin/killall mpd &>/dev/null
			/bin/killall mplayer &>/dev/null
			/bin/killall squeezeslave &>/dev/null
			;;
		"CROND")
			Log "[System]" "Stopping crond process"
			/bin/killall crond &>/dev/null
			;;
		*)
			Log "[System]" "Stopping all OpenKarotz processes"
			/bin/killall led &>/dev/null
			/bin/killall ears &>/dev/null
			/bin/killall madplay &>/dev/null
			/bin/killall mpd &>/dev/null
			/bin/killall mplayer &>/dev/null
			/bin/killall squeezeslave &>/dev/null
			;;
	esac
}

# ---------------------------------------------------------------------------
# Sent HTTP response with defined headers
# ---------------------------------------------------------------------------
function SendResponse {
	DT=$1
	echo "Server: OpenKarotz WebServer 1.0"
	echo "Connection: close"
	echo "Accept-Ranges: bytes"
	#echo "Content-Length: "${#DT}
	#echo "Content-type: application/json"
	echo "Content-type: text/plain"
	echo "Access-Control-Allow-Origin: *"
	echo ""
	echo -e ${DT}
}

# ---------------------------------------------------------------------------
#
# ---------------------------------------------------------------------------
function IsSoundPlaying {
	if pidof mplayer &>/dev/null; then
		echo 1
		exit
	fi
	if pidof squeezeslave &>/dev/null; then
		echo 1
		exit
	fi
	echo 0
}

# ---------------------------------------------------------------------------
#
# ---------------------------------------------------------------------------
function PlaySound {
	#  SOUND=$1
	# TODO: Volume management
	#  -softvol -af volume=-20
	#   0  => Normal
	#   -x => Down
	#   +x => Up
	# killall mr &>/dev/null
	CHECK=$(IsSoundPlaying)
	if [ ${CHECK} -eq 0 ]; then
		KillProcess SOUNDS
		/usr/bin/madplay -q $1 &>/dev/null
	fi
}

function PlaySoundEx {
	#  SOUND=$1
	#  BG=$2
	# TODO: Volume management
	#  -softvol -af volume=-20
	#   0  => Normal
	#   -x => Down
	#   +x => Up
	CHECK=$(IsSoundPlaying)
	if [ ${CHECK} -eq 0 ]; then
		KillProcess SOUNDS
		if [ ! -f /tmp/mplayer-control ]; then
			mknod /tmp/mplayer-control p &>/dev/null
		fi
		if [ $2 -eq 1 ]; then
			mplayer -quiet -slave -include /etc/conf/mplayer.conf -input file=/tmp/mplayer-control $1 &>/dev/null &
		else
			mplayer -quiet -slave -include /etc/conf/mplayer.conf -input file=/tmp/mplayer-control $1 &>/dev/null
		fi
	fi
}

# ---------------------------------------------------------------------------
#
# ---------------------------------------------------------------------------
function StartTagRecording {
	echo "1" >${CNF_DATADIR}/Run/rfid.record
	PlaySound ${CNF_DATADIR}/Voice/Rfid_Start_Record.mp3 1 &>/dev/null
}

# ---------------------------------------------------------------------------
#
# ---------------------------------------------------------------------------
function StopTagRecording {
	rm -f ${CNF_DATADIR}/Run/rfid.record &>/dev/null
	PlaySound ${CNF_DATADIR}/Voice/Rfid_Stop_record.mp3 1 &>/dev/null
	LedsRestore
}
