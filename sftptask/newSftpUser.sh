#!/bin/bash

sudo adduser $1
sudo mkdir /home/$1/log
sudo mkdir /sftp_users/$1
sudo chown -R $1:$1 /sftp_users/$1

ssh-keygen
sudo mkdir /home/$1/.ssh/
sudo mv ~/.ssh/id_rsa.pub /home/$1/.ssh/authorized_keys
sudo chown -R $1:$1 /home/$1
sudo mv ~/.ssh/id_rsa /home/ubuntu/.ssh/$1.pem

str='command="pysftpjail \/sftp_users\/yangshiwuxi",no-port-forwarding,no-x11-forwarding,no-agent-forwarding'
str=`echo $str | sed "s/yangshiwuxi/$1/"`
sudo sed -i "1s/^/$str /" /home/$1/.ssh/authorized_keys
