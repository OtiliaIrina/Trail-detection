The CHEOPS mission, dedicated to studying exoplanets, has encountered some of those trails in its images.
These trails could be used as a valuable insight in understanding the growing density of objects in low Earth orbit and their distribution.
Indeed, the increase in deployment of satellites for diverse purposes like communication and Earth observation has raised concerns about how crowded the Earth orbits are, especially low Earth orbit. 
This high density of objects poses collision risks, leading to more debris and potential damage to other satellites due to their high velocities, threatening the sustainability of space activities. 
Since CHEOPS is in a Sun-synchronous low Earth orbit and has minimal interference from Earth shadows it is in an advantageous situation for spotting nearby objects.

The detection algorithm, designed in Python, processes individual FITS images within a data cube employing various pre-processing techniques, including median filtering and Canny edge detection.
A Hough transform is then applied to find and characterize the trails, extracting essential information such as their position, angles and brightness. 
The algorithm's performance was assessed across various parameters, highlighting its proficiency in detecting most trails.
However, is also showcased its limitations in identifying low-brightness and grazing trails, as well as determining that specific trail angles are harder to detect.

To assess the completeness of the code, a series of simulated images were generated with variations in brightness, trail angle, and position. These images underwent evaluation using the detection code to gauge its effectiveness in identifying streaks. The simulated images were created by manipulating a data cube from the CHEOPS database, devoid of trails, and a white PSF fits image from the CHEOPS archive. The process involved applying a sequence of operations to each frame using Python programming. These operations included the use of a kernel for blurring the Point Spread Function (PSF) along a specified line, normalization of the kernel's amplitude, introduction of a random angle rotation, and multiplication by a randomly generated brightness factor. The resulting streak was integrated with the central star to construct the final simulated image.

A crucial aspect, the "impact parameter," determining the trail's position within the image, is vital for the study's completion. To assess the code's capability in detecting trails grazing within an image, enhancements were made to the simulated image generation code. This involved incorporating an inputted impact parameter to evaluate the code's performance under minimal trail presence.
