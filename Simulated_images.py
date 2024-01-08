from astropy.io import fits
import random
import cv2
import numpy as np
import os
import astropy.io.fits as pyfits
import matplotlib.pyplot as plt

# Path to your data cube FITS file
input_cube = '/Users/otilia/Desktop/cube.fits'

PSF_path = '/Users/otilia/Desktop/ds9.fits'
PSF = fits.open(PSF_path)
PSF_data = PSF[0].data.astype(np.float32)

# Define the path to the desktop
desktop_path = '/Users/otilia/Desktop/'

# Create a folder for the FITS files if it doesn't exist
folder_name = 'Images streaks'
folder_path = os.path.join(desktop_path, folder_name)
os.makedirs(folder_path, exist_ok=True)


# Create a 400x400 zero matrix
psf_400 = np.zeros((400, 400))

# Calculate the starting point to place PSF_data in the center
start_x = (400 - PSF_data.shape[0]) // 2
start_y = (400 - PSF_data.shape[1]) // 2

# Define the end points to place PSF_data
end_x = start_x + PSF_data.shape[0]
end_y = start_y + PSF_data.shape[1]

# Place PSF_data in the center of the zero matrix
psf_400[start_x:end_x, start_y:end_y] = PSF_data

def streak(random_angle, brightness):
    kernel_length = 400
    kernel = np.zeros((kernel_length, kernel_length))
    kernel[int((kernel_length - 1) / 2), :] = 1  # Create a horizontal kernel

    # Rotate the kernel to a random angle
    rotation_matrix = cv2.getRotationMatrix2D((kernel_length // 2, kernel_length // 2), random_angle, 1) #generates a rotation matrix using cv2.getRotationMatrix2D that rotates the kernel around its center ((kernel_length // 2, kernel_length // 2)) by the random_angle.
    
    #Applies the rotation transformation to the kernel using cv2.warpAffine. The resulting kernel is the streak rotated by the random_angle.
    kernel = cv2.warpAffine(kernel, rotation_matrix, (kernel_length, kernel_length))
    
    kernel = kernel / np.max(kernel)
    kernel = kernel * brightness

    return kernel


# Open the data cube FITS file
with fits.open(input_cube, mode='update') as hdulist:
    cube_header = hdulist[1].header
    cube_data = hdulist[1].data
    modified_cube = np.zeros_like(cube_data)
    size = cube_data.shape[0]
    random_angles = np.zeros(size)
    outfits = pyfits.open(input_cube)
    
    for i in range(cube_data.shape[0]):
        output_cube = os.path.join(folder_path, f"{i}.fits")
        
        # Set random brightness 
        brightness = random.randint(1,65500)
        # Generate angles in steps of 10 from 0 to 180  
        random_angle = random.randint(0, 360)  # Generate a random angle between 0 and 180
        # print(random_angle)
        
        # Generate a single random value for impact parameter (rho)
        # 100 is grazing and 0 is perfectly through middle
        rho = random.randint(0, 100)
        alpha= 90 - random_angle
        # print('rho',rho)

        # The sin()/cos() function in Python's NumPy library takes angles in radians, not degrees. 
        # To convert degrees to radians, you can use the numpy.deg2rad() function.
        angle_rad = np.deg2rad(alpha)
        sin_value = np.sin(angle_rad)
        cos_value = np.cos(angle_rad)
        
         # Calculating the coordinates of the center of the cropped image
        cropped_center_y = int(200 - rho * sin_value )
        cropped_center_x = int(200 - rho *  cos_value)
        
        # print('cropped_center_x:',cropped_center_x)
        # print('cropped_center_y:',cropped_center_y)
         
        #Calculating the start of the cropped image
        crop_x = cropped_center_y -100
        crop_y = cropped_center_x -100
        

        streak_kernel = streak(random_angle, brightness)
        streak_result = cv2.filter2D(psf_400, -1, streak_kernel)
        

        cropped_image = streak_result[crop_x:crop_x + 200, crop_y:crop_y + 200]
        
        # Define a circular mask for the cropped image
        height, width = cropped_image.shape
        center_x, center_y = width // 2, height // 2
        radius = min(center_x, center_y)
        y, x = np.ogrid[:height, :width]
        mask = ((x - center_x) ** 2 + (y - center_y) ** 2 <= radius ** 2)
        cropped_image[~mask] = 0.0
   
        modified_image = cube_data[i] + cropped_image
        modified_image = np.nan_to_num(modified_image, copy=False, nan=0.0, posinf=0.0, neginf=0.0)
        plt.imshow(modified_image, cmap='gray')
        plt.axis('off')
        
        # Save the modified cube to a new FITS file with the updated header
        modified_cube[i] = modified_image
        outfits[1].data[i, :, :] = modified_image
        outfits[1].header= cube_header
        # cube_header['ANGLE'] = (random_angle, 'degrees')
        # cube_header['IMPACT'] = (rho, 'distance to center')
        
        header = cube_header.copy()  # Create a new header for each file
        header.append(('IMPACT', rho), end=True)  # Set 'Impact' value for this specific file
        header.append(('ANGLE', random_angle), end=True)  # Set 'Random_Angle' value for this specific file
        # header['ANGLE'] = (random_angle, 'degrees')
        # header['IMPACT'] = (rho, 'distance to center')
        outfits.writeto(output_cube, overwrite=True)
   
    # Now, save only the last modified cube
    last_output_cube = os.path.join(folder_path, f"{i}-imapct.fits")
    outfits.writeto(last_output_cube, overwrite=True)
    
    # Delete all previously generated FITS files except the last one
    files_to_delete = [f for f in os.listdir(folder_path) if f.endswith('.fits') and f != f"{i}-impact.fits"]
    for file in files_to_delete:
        os.remove(os.path.join(folder_path, file))
    