<h1> Autodesk Fusion - Horn Antenna Generator </h1> 

This is a Autodesk Fusion utility script to automatically generate a horn antenna based on simple dimension parameters.

<h3> Example </h3> 
Using the following parameters:
<pre>convertFactor = 10          # Convert mm to cm
a = 10.668  / convertFactor # Waveguide width [a] (mm)
b = 4.318   / convertFactor # Waveguide height [b] (mm)
A = 60  / convertFactor     # Horn aperture width (mm)
B = 45  / convertFactor     # Horn aperture height (mm)
L = 120  / convertFactor    # Total length of horn antenna (mm)
L1 = 10 / convertFactor     # Length of the waveguide section at the base of the horn antenna (mm)
t = 2   / convertFactor     # Horn wall thickness (mm)</pre>


<p align="center">
  <img src="https://raw.githubusercontent.com/saulcarvalho/AutodeskFusion_HornAntenna_Generator/main/assets/Standard_PyramidalHornAntenna_WR42_20dBi.png"/> </br>
  <b>Figure 1.</b> A standard gain horn antenna with WR42 waveguide channel entrance and a gain of 20 dBi.
</p>
