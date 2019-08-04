#!/bin/bash

host_name=$(hostname)

usage() {
    echo "Usage: ./systemd_install.sh -e executable_name
Example: ./systemd_install.sh -e ${host_name^}"
}
confirm() {
    read -rp " > ${1} [y/n] " yn
    case "$yn" in
        [yYsS])
            true ;;
        *) 
            false ;;
    esac
}

while getopts 'e:' flag
do
    case "${flag}" in
        e) executable=${OPTARG} ;;
        *) usage
            exit 1 ;;
    esac
done

if ! command -v ${executable} > /dev/null
then
    echo "Can't find executable ${executable} in path"
    usage
    exit 1
fi

if [[ $# -le 1 ]]
then
    usage
    exit 1
fi

# Small bash script to create a systemd unit with to start the 
# bot on start as a daemon
# TODO: make it into part of the --install command?
unitname=pybliotecario
username=$USER
python_exe=$(which python3)
pybliotecario_exe=$(which ${executable})
systemd_file=/usr/lib/systemd/system/${unitname}.service

# Check whether the service already exists
if [[ -f "${systemd_file}" ]]
then
    echo "Unit ${unitname} already exists"
    if ! confirm "Overwrite previous unit?"
    then
        exit 1
    fi
fi

# Now select the different options
extra_options=""

echo "Sometimes badly formed commands or network errors can make the bot fail
The bot can just exit on failure or just ignore the error"
if confirm "Do you want to ignore errors?" 
then
    extra_options="${extra_options} --clear_incoming"
    restart_on="
Restart=on-failure
RestartSec=5s"
fi

echo "You can receive the IP of the host computer every time the unit starts"
if confirm "Do you want to recieve a msg with the IP of the computer?"
then
    extra_options="${extra_options} --my_ip Estoy despierto, ip: "
fi

tmpfile=.pybliounit.unit
echo "[Unit]
Description=My Script Service
After=multi-user.target

[Service]
User=${username}
Type=simple
ExecStart=${python_exe} ${pybliotecario_exe} -d ${extra_options}
${restart_on}

[Install]
WantedBy=multi-user.target"  > ${tmpfile}

# From now on we need sudo
sudo mv ${tmpfile} ${systemd_file}
# Kill it in case it was already there
if systemctl is-active --quiet ${unitname} > /dev/null
then
    echo "${unitname} was already active, restarting"
    sudo systemctl stop ${unitname}
    sudo systemctl disable ${unitname}
fi
sudo systemctl daemon-reload
sudo systemctl enable ${unitname}
sudo systemctl start ${unitname}
