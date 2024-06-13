#!bin/bash

# This script's goal is to create a backup of your .bashrc () -> using crontab : every week ) and store it in a folder "Folder_backup_bashrc"

user=$(whoami)
path_home_user=/home/cfd/$user
current_date=$(date +"%Y-%m-%d")

cp $path_home_user/.bashrc $path_home_user/bashrc_backup_$current_date

if test -d $path_home_user/Folder_backup_bashrc; then
    mv $path_home_user/bashrc_backup_$current_date $path_home_user/Folder_backup_bashrc
else 
    mkdir $path_home_user/Folder_backup_bashrc
    mv $path_home_user/bashrc_backup_$current_date $path_home_user/Folder_backup_bashrc
fi