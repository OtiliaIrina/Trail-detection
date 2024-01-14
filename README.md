The CHEOPS mission, dedicated to studying exoplanets, has encountered some of those trails in its images.
These trails could be used as a valuable insight in understanding the growing density of objects in low Earth orbit and their distribution.
Indeed, the increase in deployment of satellites for diverse purposes like communication and Earth observation has raised concerns about how crowded the Earth orbits are, especially low Earth orbit. 
This high density of objects poses collision risks, leading to more debris and potential damage to other satellites due to their high velocities, threatening the sustainability of space activities. 
Since CHEOPS is in a Sun-synchronous low Earth orbit and has minimal interference from Earth shadows it is in an advantageous situation for spotting nearby objects.

The detection algorithm, designed in Python, processes individual FITS images within a data cube employing various pre-processing techniques, including median filtering and Canny edge detection.
A Hough transform is then applied to find and characterize the trails, extracting essential information such as their position, angles and brightness. 
The algorithm's performance was assessed across various parameters, highlighting its proficiency in detecting most trails.
However, is also showcased its limitations in identifying low-brightness and grazing trails, as well as determining that specific trail angles are harder to detect.


