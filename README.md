# SDN-Controller

Controller for Software-Defined Network with live DASHboard using DASH

This controller was designed for any possible sdn topology to
1. Calculate shortest path for the request and then assign the path (flow)
2. Detecting link failure and assign another available path

System : Ubuntu 20.04 amd64
ps. default password of ubuntu is changeme

How to run
1. Preparing python environment according to the requirement.txt
2. Running 3 terminal of python which consist of
   1. Running Ryu-Controller using command
        sudo ryu-manager --observe-links SWM6.py
   2. Running web-server using command
        sudo python3 DASH2.py
   3. Running MiniEdit using command
        sudo python3 ~/mininet/examples/miniedit.py
3. In the MiniEdit, creating network topology using Host and Openflow Switches
4. Connecting all Openflow Switches to SDN-Controller and don't forget to change the controller type to Remote Controller (in Property menu)
5. Edit > Preferences , remove tick from OpenFlow 1.0 and ticking OpenFlow 1.3 instead
6. Now Mininet setup is finished, click Run miniedit (if things work correctly, Ryu-Controller should show log in its terminal)
7. Openning Web-GUI using localhost::8050 (8050 is default DASH port), you need to re-arrange the GUI by your self, by dragging the icon to whatever place you want 

FAQ

Q1: Unable to run DASH2.py due to existed port already using

A1: Open task manager, searching "dash", removing all the task related to Python-Dash and then running DASH2.py again

Q2: Only switches shown in the Web-GUI, not Hosts

A2: You need to ping, i.e., host1 ping host2, for all the host in topology for controller to detect all the hosts (please only use different host from previous ping, for example, fist ping is host1-host2, next ping is host3-host4, to avoid any not-yet fixed bugs lol)

Q3: Ryu not working properly, it can't detecting disconnect link

A3: Don't forget to put --observe-links inthe running command

Q4: Ryu not working properly, (not the same as Q3)

A4: When ever running this project after some re-configuration in whatever part, running command
      sudo mn -c
   in order to clean all the virtual network process

Q5: Can't close Miniedit, the GUI seems crashed

A5: Idk, probably need to restart the OS, or just run the new MiniEdit is also fine (don't forget to sudo mn -c)

Q6: PC and Switch icon don't show properly

A6: Something might happen with the image that i put in my google-drive, try import new image instaead, using links or just image in your pc (fix at line 140-150)
