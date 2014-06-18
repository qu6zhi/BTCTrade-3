#!/bin/sh
date
ps aux|grep "python"|grep -v grep > /dev/null
if [ $? -eq 0 ]
then
   echo "Process is OK"
   if [ -f "/home/prog1/code/out1.log" ]
   then
      diff ~/code/out1.log ~/out1.log > diff.log
      if [ $? -ne 0 ]
      then
	 echo "File is OK"
	 cp /home/prog1/code/out1.log /home/prog1/out1.log
      else
	 echo "No activity, kill and restart..."
	 killall -9 python
	 /home/prog1/code/go.sh
      fi
   else
      echo "No file, kill and restart..."
      killall -9 python
      /home/prog1/code/go.sh
   fi
else
   echo "No python process, restart..."
   /home/prog1/code/go.sh
fi
