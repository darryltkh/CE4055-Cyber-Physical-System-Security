# CE4055 Cyber-Physical System Security Project (AY22/23 Sem 2)
### Team Name: Cyberbullies
### Team Members: Ang Kai Jun, Lee Zhe Ren, Tan Kah Heng Darryl

----

This is a lab exercise to understand how power analysis side channel attacks can happen on an embedded device. The power traces of an AES-128 encryption operation is recorded, along with the plaintext. The aim is to guess the secret key from the power traces and the plaintext.

Files in this project:
- images folder --> Stores all graphs for plot 1 and plot 2 requirement.
- waveform.csv --> The waveform.csv file that is generated after collecting power traces from the SCA board device.
- cpa_key_prediction.py --> Main python script. Run to get the predicted key used in this AES operation.
- cpa_plot1.py --> Run this script to create the graphs for plot 1 requirement.
- cpa_plot2.py --> Run this script to create the graphs for plot 2 requirement.

Please submit a ticket to Darryl Tan (dtan103@e.ntu.edu.sg) if you need help.
