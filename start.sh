#!/bin/sh
cd "/home/weipeng/Freenove_Big_Hexapod_Robot_Kit_for_Raspberry_Pi/Code/Server"
pwd
sleep 5
sudo cp point.txt /home/pi
sudo python main.py -nts
while [[ -z $(ls /dev/input/js0 2> /dev/null) ]]
do 
	sleep 1
	echo "Waiting for bt controller"
done
cd "/home/weipeng/Freenove_Big_Hexapod_Robot_Kit_for_Raspberry_Pi/Code/Client"
python controller_client.py

