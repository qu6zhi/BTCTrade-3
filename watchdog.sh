#!/bin/sh
date
ps aux|grep "python"|grep -v grep >/dev/null
if [ $? -eq 0 ]
then
   echo "Process is OK"
   diff ~/code/out.log ~/out.log >/dev/null
   if [ $? -ne 0 ]
   then
      echo "File is OK"
      cp ~/code/out.log ~/out.log
   else
      echo "No activity, kill and restart..."
      killall -9 python
      ~/code/go.sh
   fi
else
   echo "No python process, restart..."
   ~/code/go.sh
fi
