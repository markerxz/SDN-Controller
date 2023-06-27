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
7. Openning Web-GUI using localhost::8050 (8050 is default DASH port)

FAQ
Q1. Unable to run DASH2.py due to existed port already using
A1. Open task manager, searching "dash", removing all the task related to Python-Dash and then running DASH2.py again

Q2. 
A2.

Q3. Ryu not working properly, it can't detecting disconnect link
A3. Don't forget to put --observe-links inthe running command
