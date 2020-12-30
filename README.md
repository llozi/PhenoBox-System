# Fork of the original PhenoBox-System repo of the Gregor-Mendel-Institute
[Original Repo](https://github.com/Gregor-Mendel-Institute/PhenoBox-System "PhenoBox-System, Gregor-Mendel-Institute")

Changes include the design of a printed circuit board to interface the Raspberry Pi (fully electronic,
no electro-mechanical elements) to facilitate the wiring.

The interface board includes a MOSFET switch for controlling the illumination. It may be used to on/off switch 
or even control the illumination intensity using PWM.

The interface board requires a few changes in the assignment of the GPIO lines.

A few simple python scripts have been added to test the workings of the interface board.

For more details on the modifications check [this fork's Wiki](https://github.com/llozi/PhenoBox-System/wiki).

Below follows the original README.md.

# PhenoBox-System
The “Phenobox”, a flexible, automated, open-source plant phenotyping solution

This is the home of all the source code for our PhenoBox/PhenoPipe system. 

Original Publication: https://nph.onlinelibrary.wiley.com/doi/abs/10.1111/nph.15129

This project is still under developement and we have already planned many improvements.
If you encounter any problems feel free to contribute to this project and help us create a great open source phenotyping solution.

For further reference please use the Wiki pages of this repository. If you have any issues either use the Github Issue page or write an email to sebastian.seitner@vbcf.ac.at
