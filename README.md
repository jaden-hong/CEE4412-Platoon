# CEE4412-Platoon
Enabling pi-cars to form a platoon and drive through roads


process:
ssh into pi cars the:

(lead car)
BaseCar.py
LeadCar2.py
EdmundStop.py
AutoDriveDraft.py

haarcascade_frontalface_default.xml
stop_data.xml

into the Freenove../Server/Code/ folder

sudo python LeadCar2.py 

(follow car)
BaseCar.py
followCar.py


lead car will run, stop when it sees a stop sign for 1.5 second, then continue along.
if follow car is lagging or faces an obstacle then it will stop it and the lead car until it is clear



