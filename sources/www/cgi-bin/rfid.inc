#!/bin/bash

source /www/cgi-bin/url.vera
source /www/cgi-bin/url.eedomus

CURL_BASE="curl -g --connect-timeout 30 -o /tmp/curlout -s -L -k"

# ---------------------------------------------------------------------------
# ACTION TYPE
# ---------------------------------------------------------------------------
RFID_ACTION_TYPE_VERA=1
RFID_ACTION_TYPE_EEDOMUS=2
RFID_ACTION_TYPE_URL=3
RFID_ACTION_TYPE_ZIBASE=4
RFID_ACTION_TYPE_KAROTZ=5
RFID_ACTION_TYPE_CALAOS=6
RFID_ACTION_TYPE_PLUGIN=7
RFID_ACTION_USER_DEFINED_TYPE=99

# ---------------------------------------------------------------------------
# Check if .rfid file exists in the correct directory
# ---------------------------------------------------------------------------
function CheckMandatoryTagId {
	DIR_NAME=$1
	TAG_ID=$2
	if [ ! -d "${DIR_NAME}" ]; then
		Log "[Rfid]" "Missing directory: ('${DIR_NAME}')" 1
		DATA='{"return":"1","msg":"Missing '${DIR_NAME}' directory."}'
		SendResponse "${DATA}"
		exit 0
	fi
	if [ ! -e "${DIR_NAME}/${TAG_ID}.rfid" ]; then
		Log "[Rfid]" "Tag ID not found" 1
		DATA='{"return":"1","msg":"Tag ID not found."}'
		SendResponse "${DATA}"
		exit 0
	fi
}

# ---------------------------------------------------------------------------
# Returns param value from the file or a default value
# ---------------------------------------------------------------------------
function ReadParam {
	FILE_NAME=$1
	DEFAULT_VALUE=$2
	if [ -e "${FILE_NAME}" ]; then
		cat ${FILE_NAME}
	else
		echo -n ${DEFAULT_VALUE}
	fi
}

# ---------------------------------------------------------------------------
#
# ---------------------------------------------------------------------------
function GetCmdName {
	RFID_CMD_NAME=""
	case $1 in
		1) RFID_CMD_NAME="VERA" ;;
		2) RFID_CMD_NAME="EEDOMUS" ;;
		3) RFID_CMD_NAME="URL" ;;
		4) RFID_CMD_NAME="ZIBASE" ;;
		5) RFID_CMD_NAME="KAROTZ" ;;
		6) RFID_CMD_NAME="CALAOS" ;;
		7) RFID_CMD_NAME="PLUGIN" ;;
		*) RFID_CMD_NAME="Unknown" ;;
	esac
	echo ${RFID_CMD_NAME}
}

# ---------------------------------------------------------------------------
#
# ---------------------------------------------------------------------------
function GetCurlError {
	CURL_ERR=""
	case $1 in
		1) CURL_ERR="Unsupported protocol." ;;
		2) CURL_ERR="Initialization failed or option not available." ;;
		3) CURL_ERR="URL has wrong format." ;;
		5) CURL_ERR="DNS didn't return proxy IP." ;;
		6) CURL_ERR="DNS didn't return IP for host." ;;
		7) CURL_ERR="Connection failed." ;;
		8) CURL_ERR="FTP error." ;;
		9) CURL_ERR="A service was denied by the server due to lack of access when login fails this is not returned." ;;
		11) CURL_ERR="FTP error." ;;
		13) CURL_ERR="FTP error." ;;
		14) CURL_ERR="FTP error." ;;
		15) CURL_ERR="FTP error." ;;
		17) CURL_ERR="FTP set command failed." ;;
		18) CURL_ERR="Only a part of the file was downloaded." ;;
		19) CURL_ERR="File not found." ;;
		21) CURL_ERR="quote command failure" ;;
		22) CURL_ERR="HTTP returned an error." ;;
		23) CURL_ERR="Write error." ;;
		25) CURL_ERR="failed upload command" ;;
		26) CURL_ERR="couldn't open/read from file" ;;
		27) CURL_ERR="Out Of memory" ;;
		28) CURL_ERR="the timeout time was reached" ;;
		30) CURL_ERR="FTP PORT operation failed" ;;
		31) CURL_ERR="the REST command failed" ;;
		33) CURL_ERR="RANGE command didn't work" ;;
		34) CURL_ERR="HTTP Post failed." ;;
		35) CURL_ERR="wrong when connecting with SSL" ;;
		36) CURL_ERR="couldn't resume download" ;;
		37) CURL_ERR="Failed to read file." ;;
		38) CURL_ERR="LDAP can't connect." ;;
		39) CURL_ERR="LDAP Search failed." ;;
		41) CURL_ERR="Function not found." ;;
		42) CURL_ERR="Transfer aborted with CURL.Cancel." ;;
		43) CURL_ERR="Bad parameters." ;;
		45) CURL_ERR="CURL.OptionInterface failed" ;;
		47) CURL_ERR="catch endless re-direct loops" ;;
		48) CURL_ERR="User specified an unknown option" ;;
		49) CURL_ERR="Malformed telnet option" ;;
		51) CURL_ERR="peer's certificate or fingerprint wasn't verified fine" ;;
		52) CURL_ERR="when this is a specific error" ;;
		53) CURL_ERR="SSL crypto engine not found" ;;
		54) CURL_ERR="can not set SSL crypto engine as default" ;;
		55) CURL_ERR="failed sending network data" ;;
		56) CURL_ERR="failure in receiving network data" ;;
		58) CURL_ERR="problem with the local certificate" ;;
		59) CURL_ERR="couldn't use specified cipher" ;;
		60) CURL_ERR="problem with the CA cert (path?)" ;;
		61) CURL_ERR="Unrecognized transfer encoding" ;;
		62) CURL_ERR="Invalid LDAP URL" ;;
		63) CURL_ERR="Maximum file size exceeded" ;;
		64) CURL_ERR="Requested FTP SSL level failed" ;;
		65) CURL_ERR="Sending the data requires a rewind that failed" ;;
		66) CURL_ERR="failed to initialise ENGINE" ;;
		67) CURL_ERR="user, password or similar was not accepted and we failed to login" ;;
		68) CURL_ERR="file not found on server" ;;
		69) CURL_ERR="permission problem on server" ;;
		70) CURL_ERR="out of disk space on server" ;;
		71) CURL_ERR="Illegal TFTP operation" ;;
		72) CURL_ERR="Unknown transfer ID" ;;
		73) CURL_ERR="File already exists" ;;
		74) CURL_ERR="No such user" ;;
		75) CURL_ERR="conversion failed" ;;
		76) CURL_ERR="caller must register conversion callbacks" ;;
		77) CURL_ERR="could not load CACERT file, missing or wrong format" ;;
		78) CURL_ERR="remote file not found" ;;
		79) CURL_ERR="error from the SSH layer" ;;
		80) CURL_ERR="Failed to shut down the SSL connection" ;;
		81) CURL_ERR="socket is not ready for send/recv, wait till it's ready and try again." ;;
		82) CURL_ERR="could not load CRL file, missing or wrong format." ;;
		83) CURL_ERR="Issuer check failed." ;;
		84) CURL_ERR="a PRET command failed" ;;
		85) CURL_ERR="mismatch of RTSP CSeq numbers" ;;
		86) CURL_ERR="mismatch of RTSP Session Identifiers" ;;
		87) CURL_ERR="unable to parse FTP file list" ;;
		88) CURL_ERR="chunk callback reported error" ;;
		*) CURL_ERR="Unknown error" ;;
	esac
	echo ${CURL_ERR}
}

# ---------------------------------------------------------------------------
#
# ---------------------------------------------------------------------------
function GetRfidTypeName {
	RFID_TYPE_NAME=""
	case $1 in
		1) RFID_TYPE_NAME="FLATANOZ" ;;
		2) RFID_TYPE_NAME="NANOZTAG" ;;
		3) RFID_TYPE_NAME="ZSTAMPS" ;;
		15) RFID_TYPE_NAME="KEYRING" ;;
		*) RFID_TYPE_NAME="UNKNOWN" ;;
	esac
	echo ${RFID_TYPE_NAME}
}

# ---------------------------------------------------------------------------
#
# ---------------------------------------------------------------------------
function GetRfidColorName {
	RFID_COLOR_NAME=""
	case $1 in
		1) RFID_COLOR_NAME="RED" ;;
		2) RFID_COLOR_NAME="BLUE" ;;
		3) RFID_COLOR_NAME="GREEN" ;;
		4) RFID_COLOR_NAME="YELLOW" ;;
		5) RFID_COLOR_NAME="PINK" ;;
		6) RFID_COLOR_NAME="BLACK" ;;
		7) RFID_COLOR_NAME="GREY" ;;
		8) RFID_COLOR_NAME="ORANGE" ;;
		9) RFID_COLOR_NAME="PURPLE" ;;
		10) RFID_COLOR_NAME="WHITE" ;;
		51) RFID_COLOR_NAME="BROWN" ;;
		*) RFID_COLOR_NAME="UNKNOWN" ;;
	esac
	echo ${RFID_COLOR_NAME}
}

function BuildZibaseUrl {
	#  IP=$1
	#  CMD=$2
	#   URLONLY=3
	ZURL='http://'$1${ZIBASE_BASE_URL}$2
	Log "[Rfid]" "Building URL: ${ZURL}"
	if [ $3 -ne 1 ]; then
		printf -v ZTEMP '%s "%s"' "${CURL_BASE}" "${ZURL}"
		ZURL=${ZTEMP}
		Log "[Rfid]" "Adding Curl prefix: " "${ZURL}"
	fi
	echo -n "${ZURL}"
}

function BuildVeraUrl {
	#  IP=$1
	#  SCENE=$2
	#  URLONLY=$3
	VERAURL='http://'$1${VERA_BASE_URL}$2
	Log "[Rfid]" "Building URL: ${VERAURL}"
	if [ $3 -ne 1 ]; then
		printf -v VERATEMP '%s "%s"' "${CURL_BASE}" "${VERAURL}"
		VERAURL=${VERATEMP}
		Log "[Rfid]" "Adding Curl prefix: " "${VERAURL}"
	fi
	echo -n "${VERAURL}"
}

function BuildEeDomusUrl {
	#  IP=$1
	#  MACRO=$2
	#  USER=$3
	#  PASSWORD=$4
	#  URLONLY=$5
	#  REMOTE=$6   (Call via eedomus Portal)
	if [ $6 -ne 1 ]; then
		Log "[Rfid]" "Eedomus portal call"
		EEPROTOCOL="https"
		EEHOST="api.eedomus.com"
		EEPATH=""
	else
		Log "[Rfid]" "Eedomus local call"
		EEPROTOCOL="http"
		EEHOST=$1
		EEPATH="/api"
	fi
	EEURL="${EEPROTOCOL}://${EEHOST}${EEPATH}${EEDOMUS_BASE_URL}&macro=$2&api_user=$3&api_secret=$4"
	Log "[Rfid]" "Building URL: ${EEURL}"
	if [ $5 -ne 1 ]; then
		printf -v EETEMP '%s "%s"' "${CURL_BASE}" "${EEURL}"
		EEURL=${EETEMP}
		Log "[Rfid]" "Adding Curl prefix: " "${EEURL}"
	fi
	echo -n "${EEURL}"
}

function BuildUrl {
	#  URL=$1
	#  PARAM=$2
	#  USER=$3
	#  PASSWORD=$4
	#  URLONLY=$5
	LURL=$1
	if [ -n "$2" ]; then
		LURL="${LURL}?$2"
	fi
	#TODO Should verify if $3 and $4 are correctly used when $5 == 1
	if [ -n "$3" ]; then
		Log "[Rfid]" "Building URL (Auth): ${LURL} ($3:$4)"
	else
		Log "[Rfid]" "Building URL: ${LURL}"
	fi
	if [ $5 -ne 1 ]; then
		if [ -n "$3" ]; then
			Log "[Rfid]" "==>" "$3:$4"
			printf -v UTEMP '%s --user %s:%s "%s"' "${CURL_BASE}" "$3" "$4" "${LURL}"
		else
			printf -v UTEMP '%s "%s"' "${CURL_BASE}" "${LURL}"
		fi
		LURL=${UTEMP}
		Log "[Rfid]" "Adding Curl prefix: " "${LURL}"
	fi
	echo -n "${LURL}"
}

function GetUrl {
	#  URL=$1
	#  USER=$2
	#  PASS=$3
	#  PARAM=$4
	if [ -z "$2" ]; then
		# URL=$(echo '${CURL_BASE}  "'$1'"' )
		printf -v UTEMP '%s "%s"' "${CURL_BASE}" "$1"
		URL=${UTEMP}
	else
		printf -v UTEMP '%s --user %s:%s "%s"' "${CURL_BASE}" "$2" "$3" "$1"
		URL=${UTEMP}
	fi
	Log "[Rfid]" "Calling URL:" "${URL}"
	eval ${URL}
	echo $?
}
