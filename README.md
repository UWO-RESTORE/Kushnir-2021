# Exploring uncertainty in thermodynamic modeling of the lead carbonate aqueous system.
## Kushnir, C and Robinson, C.
## Published: 2021

###### Note to Users of this Repository:
Everything you need to replicate the factorial run as described in Kushnir (2021) has been provided in /Code and /Code/Example User Files. This includes the phreeqc-no-gui.exe file that was used to run all the phreeqc files. 

All coding was done with the intention of only being seen by 1 person in a utilitarian fashion. Please excuse the single file format and the confusing file structure. I learned how to program python while doing this, so somethings may be less than ideal.

###### The gist of the program is to:
1. Create a series of phreeqc files (.txt) that change speicific LogKs of species within the file structure itself. This is created according to a standard full factorial.
2. Run the .txt phreeqc files through the preeqc-no-gui.exe to get model results.
3. Coallate the results of specific values (such as Pb or pH) into a single file that can be cross referenced with the standard full factorial.
4. Calculate the Main Effects and Interaction Effects using the coallated results and full facotorial of LogK values.
5. Graph the Main Effects and Interaction Effects based on calculations.
6. Match experimental data to the coallated results to determine which sets of LogKs achieve the experimental results within a specified tolerance of standard deviation.
