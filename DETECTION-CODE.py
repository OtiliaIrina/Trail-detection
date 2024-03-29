

import numpy as np
import pandas as pd
from astropy.io import fits
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import glob
from astropy.io import ascii
import cv2
import os
import pickle
from astropy.time import Time
from astropy.time import TimeDelta
from scipy import interpolate
from scipy import ndimage
from astropy.stats import median_absolute_deviation
from scipy.signal import general_gaussian
from scipy import stats



def create_circular_mask(h, w, center=None, radius=None):

    if center is None: # use the middle of the image
        center = (int(w/2), int(h/2))
    if radius is None: # use the smallest distance between the center and image walls
        radius = min(center[0], center[1], w-center[0], h-center[1])

    Y, X = np.ogrid[:h, :w]
    dist_from_center = np.sqrt((X - center[0])**2 + (Y-center[1])**2)

    mask = dist_from_center <= radius
    return mask

path = "/Users/otilia/Desktop/Angles with set 2000 brightness/"
pathout = os.getcwd() + '/WinFrame/'




# Iterate through each FITS file in the folder
for file in glob.glob(os.path.join(path, '*.fits')):
    myFits = fits.open(file)
    cube = myFits[1].data
        
        
    # initialise
    totFrames = 1
    
    #  erased 'RA', 'Dec', 'Roll',
    col    = ['filename', 'OR_key', 'date', 'mjd', 'expTime', 'nexp', 'frame_index', 'los_earth_angle', 'los_sun_angle', 'latitude', 'longitude', \
    'trail_angle', 'sat_mag', 'impact_param', 'n_lines_detected', 'angle_std', 'rho_mean', 'rho_std', 'stat_theta', 'stat_rho', 'profil', 'profil_sum']
    data   = pd.DataFrame(columns = col)
    
    #erased 'RA', 'Dec'
    col_2  = ['mjd', 'los_earth_angle', 'los_sun_angle', 'latitude', 'longitude', 'expTime', 'nexp']
    all_in = pd.DataFrame(columns = col_2)
    
    
    
    
    filename    = (file).rsplit('/', 1)[-1]
    OR_key      = 'PR' + str(myFits[1].header['PROGTYPE']) + str(myFits[1].header['PROG_ID']).zfill(4) + '_TG' + str(myFits[1].header['REQ_ID']).zfill(4) + str(myFits[1].header['VISITCTR']).zfill(2)
    nexp        = myFits[1].header['NEXP']   # image stacking order
    expTime     = myFits[1].header['EXPTIME']   # exposure time[s] of individual images
    leftDarkMedian  = np.median(myFits[4].data) 
    gain            = 0.5   # very rough value, to be improved
    QE              = 0.5   # very rough value, to be improved
    
    
    
    
    #defines iFrame
    iFrame=0
    
    # Initialize a variable to count frames with trails
    frames_with_trails = 0
    
    #does a loop to check all the images that are stacked which have a streak 
    for iFrame in range(cube.shape[0]):
         imaOri = cube[iFrame, :,:]
         the_x  = np.arange(300) 
         
         # Remove hot pixels
         imaOri[np.isnan(imaOri)] = 0
         ima = cv2.medianBlur(imaOri.astype('uint16'), 5) #plot
         
         # Detect edges
         ima8b = cv2.normalize(ima, None,0,255, cv2.NORM_MINMAX, dtype=cv2.CV_8U) #plot
         edges = cv2.Canny(ima8b,1500,2000,apertureSize = 7) #plot
         
         lines = cv2.HoughLines(edges,1,np.pi/180,60)
    
      
         if lines is not None: #checks if any lines
         # Check if a trail is found in the frame
        
              print('    +++  In frame #{}, found {} lines'.format(iFrame, len(lines)))
    
              saturThreshold = 10
              SaturationFrame = (len(np.where(imaOri == np.max(imaOri))[0]) > saturThreshold)    # if more than 10 pixels are saturated in the frame, ignore it later for satCrossing detection
              if SaturationFrame:
                 print('==>  Found saturation in frame {}. Skipping this frame!!! \n'.format(iFrame))
    
              if  ((len(lines) < 100) & (not SaturationFrame)):
                  
                frames_with_trails += 1  # Increment count if a trail is found
                  
                plt.imshow(imaOri, norm=LogNorm())    ###
                truc                = (file).rsplit('/', 1)[-1]
                the_theta           = []
                the_rho             = []
        
                for j in range(len(lines)):
                    for rho,theta in lines[j]:
                        #print('Theta-----   ', theta)
                        a           = np.cos(theta)
                        b           = np.sin(theta)
                        x0          = a*rho
                        y0          = b*rho
                        the_theta.append(theta)
                        the_rho.append(rho)
                        plt.plot(the_x, (the_x-x0+y0*np.tan(np.pi-theta))/np.tan(np.pi-theta), color="white", linestyle='dashed', linewidth=1, alpha=0.5)  ###
                theta_mean          = np.mean(the_theta)
                rho_mean            = np.mean(the_rho)
                theta_std           = np.std(the_theta)
                rho_std             = np.std(the_rho)
                stat_theta          = stats.describe(the_theta)
                stat_rho            = stats.describe(the_rho)
                
                # compute the impact parameter
                x                   = np.arange(len(ima))
                y                   = (x-np.cos(theta_mean)*rho_mean + np.sin(theta_mean)*rho_mean*np.tan(np.pi-theta_mean))/np.tan(np.pi-theta_mean)  # this is the equation of the line representing the trail
                dist                = [ np.sqrt( (100 - x[i])**2 + (100 - y[i])**2)  for i in range(len(x))]    # distance between the center of the image and each point of the trail
                my_impact_param     = dist[np.where(dist == np.min(dist))[0][0]]     # actual distance in pixel 
        
                if (theta*180./np.pi < 5) | (theta*180./np.pi > 175) :
                    # check for smearing effect (nearly vertical lines)
                    print('            ==>   likely smearing for this frame...')
                    fileout = 'cube_smear_'+truc[3:59] + '_' + str(iFrame) + '.png'
                    ###plt.imshow(imaOri, norm=LogNorm())#;plt.show()
                    plt.annotate('('+str(x0) + ', ' + str(y0)+ ', ' + str(theta*180/np.pi) + ')', xy=(0.1,0.2))
                    # plt.savefig(pathout + fileout)    test
                    plt.close()
                    
                else:
    				# We have a trail in the image: Collect relevant info from SCI_RAW_SubArray
                    los_earth_angle   = myFits[9].data['LOS_TO_EARTH_ANGLE'][iFrame]
                    los_sun_angle     = myFits[9].data['LOS_TO_SUN_ANGLE'][iFrame]
                    latitude          = myFits[9].data['LATITUDE'][iFrame]
                    longitude         = myFits[9].data['LONGITUDE'][iFrame]
                    date              = myFits[9].data['UTC_TIME'][iFrame]   # time of sample (UTC)
                    mjd               = myFits[9].data['MJD_TIME'][iFrame]   # time of sample (MJD)
                    
                    # Fetch RA, Dec and Roll angle from  the SCI_RAW_Attitude file
                    #att   = fits.open(glob.glob(file.rsplit('/',1)[0] + '/CH*_SCI_RAW_Attitude_*fits')[0])
                    #ind   = np.where(np.abs(mjd-att[1].data['MJD_TIME']) == min(np.abs(mjd-att[1].data['MJD_TIME'])))
                    #RA    = att[1].data['SC_RA'][ind][0]
                    #Dec   = att[1].data['SC_DEC'][ind][0]
                    #Roll  = att[1].data['SC_ROLL_ANGLE'][ind][0]
                    
                    # # Fetch CHEOPS position from the AUX_RES_Orbit file
                    # #
                    # ind_orb_file     = np.argmin(np.abs(orb_times - Time(float(mjd), format='mjd')))    # find in which file we want to read CHEOPS' position
                    # #print('\n',Time(float(mjd), format='mjd').fits, orb_times[ind_orb_file])
                    # if (orb_times[ind_orb_file] - Time(float(mjd), format='mjd')) > 0:
                    #     ind_orb_file -= 1     # This is necessary in case the time of the exposure falls just before the start of the AUX_RES_OBR file start time
                    # #print('----- ', (orb_times[ind_orb_file] - Time(float(mjd), format='mjd')))
                    
                    # my_orb           = fits.open(orb_all[ind_orb_file])
                    # #
                    # #print('++ ', orb_all[ind_orb_file])
                    # my_orb_time_all  = Time(my_orb[1].data['EPOCH'], format='isot')
                    # ind_orb_time     = np.argmin( np.abs(my_orb_time_all - Time(float(mjd), format='mjd')) )
                    # ind_range        = ind_orb_time + np.arange(-8,8,1) 
                    # f_x = interpolate.interp1d(my_orb_time_all[ind_range].mjd, my_orb[1].data['X'][ind_range], kind='cubic')#, fill_value='extrapolate')   # extrapolation leads to crap...
                    # f_y = interpolate.interp1d(my_orb_time_all[ind_range].mjd, my_orb[1].data['Y'][ind_range], kind='cubic')
                    # f_z = interpolate.interp1d(my_orb_time_all[ind_range].mjd, my_orb[1].data['Z'][ind_range], kind='cubic')
                    # X_sat            = f_x(mjd)
                    # Y_sat            = f_y(mjd)
                    # Z_sat            = f_z(mjd)
                        
    
                        
                    #####   Compute trail brightness by rotating the image by the angle of the trail to obtain a vertical trail. Then collapse the trail with a median to estimate its brightness
                    #imaRot           = cv2.warpAffine((imaOri - leftDarkMedian) / (nexp*expTime * gain * QE), cv2.getRotationMatrix2D( (99.5 , 99.5 ) , theta_mean*180/np.pi, 1.0), (200, 200) )
                    #imaRot           = cv2.warpAffine((imaOri - leftDarkMedian) / (nexp * gain * QE), cv2.getRotationMatrix2D( (99.5 , 99.5 ) , theta_mean*180/np.pi, 1.0), (200, 200) )  # ExpTime is not relevant as the debris is not on CCD during all the exposure. Nexp is relevant though, as the trail most likely appear on only one single-frame pre-coadding.
                    imaRot           = cv2.warpAffine((imaOri - leftDarkMedian) / gain, cv2.getRotationMatrix2D( (99.5 , 99.5 ) , theta_mean*180/np.pi, 1.0), (200, 200) )  # in units of electron. Actually, Nexp is not relevant either, because we are coadding on board, not averaging...
                    h, w             = imaRot.shape[:2]
                    imaRot[~create_circular_mask(h, w, radius=99)] = np.nan
    
                  
                    psf_width        = 45   # size of the psf/mask to compute the trail brightness
                    band             = imaRot[ : ,int(100+(my_impact_param-psf_width/2)):int(100+(my_impact_param+psf_width/2))]
                    
                    # Display the boundaries of the extracted band (after rotating back the lines to the orignial orientation)   ###
                    x_left , x_right = np.repeat(int(100+(my_impact_param-psf_width/2)), 200) , np.repeat(int(100+(my_impact_param+psf_width/2)), 200)
                    y_left , y_right = np.arange(200) , np.arange(200)
                    the_angle        = theta_mean
                    plt.plot((x_left-99.5)*np.cos(the_angle) - (y_left-99.5)*np.sin(the_angle)+99.5, (x_left-99.5)*np.sin(the_angle) + (y_left-99.5)*np.cos(the_angle)+99.5, color="lightgrey", linestyle='solid', linewidth=2, alpha=0.5)
                    plt.plot((x_right-99.5)*np.cos(the_angle) - (y_right-99.5)*np.sin(the_angle)+99.5, (x_right-99.5)*np.sin(the_angle) + (y_right-99.5)*np.cos(the_angle)+99.5, color="lightgrey", linestyle='solid', linewidth=2, alpha=0.5)
                    plt.colorbar()
                    plt.tight_layout()
                    
                    med_band         = np.nanmedian(band, axis = 0)
                    med_band         = med_band - np.nanmin(med_band)
                    sat_mag          = np.nanmax(med_band)                
                    sum_band         = np.nansum(band, axis = 0)
                    sum_band         = sum_band - np.nanmin(sum_band)
                    
                                    
                    #  erased 'RA', 'Dec', 'Roll',
                    tmp = pd.DataFrame([[filename, OR_key, date, mjd, expTime, nexp, iFrame, los_earth_angle, los_sun_angle, latitude, longitude,  theta*180/np.pi, sat_mag, my_impact_param, len(lines), theta_std, rho_mean, rho_std, stat_theta, stat_rho, med_band, sum_band]], columns=col)
                    data = pd.concat([data, tmp], ignore_index=True)
                    
                    # Save the image of the frame if a satellite is spotted in the FoV
                    plt.annotate('Angle: {:.1f} deg, Brightness: {:.2f}'.format(theta_mean*180/np.pi, sat_mag), xy=(0.25,0.05), xycoords='figure fraction')
                    plt.axis('on') 
                    plt.tight_layout() # changed to on to dispaly axis 
                    fileout = 'cube_satCrossing_'+truc[3:59] + '_' + str(iFrame) + '.png'
                    plt.savefig(pathout + fileout, bbox_inches = 'tight')
                    plt.close()
                    data.to_csv(pathout+'satCross-info.csv', index=False)
                    
    
        
                if  (len(lines) >= 100) & (not SaturationFrame):
                     print('            ==>   found too many lines in this frame...')
                     fileout = 'too_many_lines_'+truc[3:59] + '_' + str(iFrame) + '.png'
                     plt.imshow(imaOri, norm=LogNorm())#;plt.show()
                     plt.savefig(pathout + fileout)
                     plt.close()
        
    
    nSat   = len(data)
    
    # print('\n\n      ===> {:4.1f}% of window frames are likely affected by satellite crossings ({}/{}) '.format(100*nSat/totFrames, nSat, totFrames))
      
    # Calculate the detection percentage
    detection_percentage = (frames_with_trails / cube.shape[0]) * 100
    
    print('\nDetected trails in {} frames out of {} ({}%)'.format(frames_with_trails, cube.shape[0], detection_percentage))
    
    # Save the detection percentage to a CSV file
    detection_data = pd.DataFrame({'Angle': [filename], 'Detection_Percentage': [detection_percentage]})
    detection_csv_path = '/Users/otilia/Desktop/b_1.csv'  # Change this path to your desired location
    if not os.path.isfile(detection_csv_path):
        detection_data.to_csv(detection_csv_path, index=False)
    else:  # If the file already exists, append to it
        detection_data.to_csv(detection_csv_path, mode='a', header=False, index=False)



    # Save 'data' and 'all_in' DataFrames using pickle with unique file names
    data_filename = 'sat-info' + file.split('/')[-1].replace('.fits', '') + '.pkl'
    with open(data_filename, 'wb') as f:
        pickle.dump(data, f)
    
    all_in_filename = 'all_in' + file.split('/')[-1].replace('.fits', '') + '.pkl'
    with open(all_in_filename, 'wb') as f:
        pickle.dump(all_in, f)
    
    # # Assuming 'n_lines_detected' and 'sat_mag' columns are in loaded_data DataFrame
    # x = data['n_lines_detected']
    # y = data['detection_percentage']
    
    # plt.figure(figsize=(8, 6))
    # plt.scatter(x, y, s=50, alpha=0.5, edgecolors='w')
    # plt.xlabel('Number of lines detected')
    # plt.ylabel('Detection Percentage')
    # plt.title('Number of Lines Found vs. Detection Percentage')
    # plt.grid(True)
    # plt.show()
