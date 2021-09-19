import os
import cv2
import numpy as np

class Stereo_Jet:

    disp_max = -100000
    disp_min = 10000
    colormap = cv2.COLORMAP_JET

    def __init__(self):
        self.sbm = cv2.StereoBM_create(numDisparities=0, blockSize=21)

    def camera_set(self,use_csi,use_usb,width,height,scale_ratio):
        cam_width = width
        cam_height = height

        flip=2

        cam_width = int((cam_width+31)/32)*32
        cam_height = int((cam_height+15)/16)*16
  
        img_width = int (cam_width * scale_ratio)
        img_height = int (cam_height * scale_ratio)

        if (use_csi==True):
            camset_1='nvarguscamerasrc sensor-id=0 ! video/x-raw(memory:NVMM), width=640, height=480, format=(string)NV12, framerate=20/1 ! nvvidconv flip-method='+str(flip)+' ! video/x-raw, width='+str(cam_width)+', height='+str(cam_height)+', format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink'
            camset_2='nvarguscamerasrc sensor-id=1 ! video/x-raw(memory:NVMM), width=640, height=480, format=(string)NV12, framerate=20/1 ! nvvidconv flip-method='+str(flip)+' ! video/x-raw, width='+str(cam_width)+', height='+str(cam_height)+', format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink'
        if (use_usb==True):
            camset_1=0
            camset_2=1
        cam_1=cv2.VideoCapture(camset_1)
        cam_2=cv2.VideoCapture(camset_2)
        return cam_1,cam_2

    def camera_read(self,cam_1,cam_2):
        ret1,img1=cam_1.read()
        ret2,img2=cam_2.read()
        return ret1,ret2,img1,img2

    def system_command(self):
        os.system("sudo systemctl restart nvargus-daemon")

    def load_calib_settings(self, img_height, GPU = True):
        
        try:
            npzfile = np.load('./calibration_data/{}p/stereo_camera_calibration.npz'.format(img_height))
        except:
            print("Camera calibration data not found in cache, file ", './calibration_data/{}p/stereo_camera_calibration.npz'.format(img_height))
            exit(0)
        try:
            npzfile1 = np.load('./calibration_data/{}p/camera_calibration_left.npz'.format(img_height))
        except:
            print("Camera calibration data not found in cache, file ", './calibration_data/{}p/camera_calibration_left.npz'.format(img_height))
            exit(0)
        try:
            npzfile2 = np.load('./calibration_data/{}p/camera_calibration_right.npz'.format(img_height))
        except:
            print("Camera calibration data not found in cache, file ", './calibration_data/{}p/camera_calibration_right.npz'.format(img_height))
            exit(0)

        leftMapX = np.array (npzfile['leftMapX'],dtype ='float32')
        leftMapY = np.array (npzfile['leftMapY'],dtype ='float32')
        rightMapX = np.array (npzfile['rightMapX'],dtype ='float32')
        rightMapY = np.array (npzfile['rightMapY'],dtype ='float32')
        leftProjection = np.array(npzfile['leftProjection'],dtype ='float32')
        rightProjection = np.array(npzfile['rightProjection'],dtype ='float32')
        gpu_leftMapX = cv2.cuda_GpuMat(leftMapX)
        gpu_leftMapY = cv2.cuda_GpuMat(leftMapY)
        gpu_rightMapX = cv2.cuda_GpuMat(rightMapX)
        gpu_rightMapY = cv2.cuda_GpuMat(rightMapY)

        if(GPU == False):
            return leftMapX,leftMapY,rightMapX,rightMapY,leftProjection,rightProjection
        else:
            return gpu_leftMapX,gpu_leftMapY,gpu_rightMapX,gpu_rightMapY,leftProjection,rightProjection

    def GPU_Remap_frame(self,img1,img2,gpu_leftMapX,gpu_leftMapY,gpu_rightMapX,gpu_rightMapY):

        gpu_frame1 = cv2.cuda_GpuMat()
        gpu_frame2 = cv2.cuda_GpuMat()

        gpu_frame1.upload(img1)
        gpu_frame2.upload(img2)
    
        gpu_grayR= cv2.cuda.cvtColor(gpu_frame1,cv2.COLOR_BGR2GRAY)
        gpu_grayL= cv2.cuda.cvtColor(gpu_frame2,cv2.COLOR_BGR2GRAY)

        grayR = gpu_grayR.download()
        grayL = gpu_grayL.download()

        imgL = cv2.cuda.remap(gpu_grayR, gpu_leftMapX, gpu_leftMapY, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
        imgR = cv2.cuda.remap(gpu_grayL, gpu_rightMapX, gpu_rightMapY, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    
        imgRcut = imgR.download()
        imgLcut = imgL.download()

        rectified_pair = (imgRcut, imgLcut)

        return rectified_pair,imgRcut,imgLcut

    def stereo_depth_map(self,rectified_pair,dm_colors_autotune,use_wls_filt,settings):
 
        disp_max = -100000
        disp_min = 10000

        dmLeft = rectified_pair[0]
        dmRight = rectified_pair[1]

        P_Flt_SZ = int(settings[0]/2)*2+1
        P_Flt_Cp = int(settings[1]/2)*2+1
        MinDisp = int(settings[2])
        NumDisp = int((settings[3]+15)/16)*16 
        Txtr_TH = int(settings[4])
        UnRatio = int(settings[5])
        Spcl_RG = int(settings[6])
        Spcl_WS = int(settings[7])
        BF_pixD = int(settings[8])
        BF_SCol = int(settings[9])
        BF_SSps = int(settings[10])
        WLS_lmbda = int(settings[11])
        WLS_sigma = float(settings[12])
        WLS_DDR = int(settings[13])
        WLS_LRS = int(settings[14])

        self.sbm.setPreFilterType(1)
        self.sbm.setPreFilterSize(P_Flt_SZ)
        self.sbm.setPreFilterCap(P_Flt_Cp)
        self.sbm.setMinDisparity(MinDisp)
        self.sbm.setNumDisparities(NumDisp)
        self.sbm.setTextureThreshold(Txtr_TH)
        self.sbm.setUniquenessRatio(UnRatio)
        self.sbm.setSpeckleRange(Spcl_RG)
        self.sbm.setSpeckleWindowSize(Spcl_WS)
    
        disparity = self.sbm.compute(dmLeft, dmRight)

        local_max = disparity.max()
        local_min = disparity.min()
        if (dm_colors_autotune):
            disp_max = max(local_max,disp_max)
            disp_min = min(local_min,disp_min)
            local_max = disp_max
            local_min = disp_min
    
        disparity_grayscale = (disparity-local_min)*((65535.0)/(local_max-local_min))
        disparity_fixtype = cv2.convertScaleAbs(disparity_grayscale, alpha=(255/(65535.0)))
        disparity_color = cv2.applyColorMap(disparity_fixtype, self.colormap)
        
        if (use_wls_filt):
            right_matcher = cv2.ximgproc.createRightMatcher(self.sbm)
            disparity_R = right_matcher.compute(dmRight,dmLeft)
            wls_filter = cv2.ximgproc.createDisparityWLSFilter(self.sbm)
            lmbda = WLS_lmbda
            sigma = WLS_sigma/100                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  
            wls_filter.setLambda(lmbda)
            wls_filter.setSigmaColor(sigma)
            wls_filter.setDepthDiscontinuityRadius(WLS_DDR)
            wls_filter.setLRCthresh(WLS_LRS)
            #filtered_disp = wls_filter.filter(disparity_grayscale, dmLeft, disparity_map_right=disparity_R)
            
            filtered_disp = wls_filter.filter(disparity_fixtype, dmLeft, disparity_map_right=disparity_R)
            disp_to_calc = ((filtered_disp.astype(np.float32)/16-MinDisp)/NumDisp)
            
            filtered_disp = cv2.bilateralFilter(filtered_disp, BF_pixD, BF_SCol, BF_SSps)
            #filtered_disp = cv2.normalize(src=filtered_disp, dst=filtered_disp, beta=0, alpha=255,norm_type=cv2.NORM_MINMAX)
            filtered_disp = np.uint8(filtered_disp)
            filtered_disp = cv2.applyColorMap(filtered_disp, self.colormap)
            
            return filtered_disp, disparity_color, disparity_grayscale, disp_to_calc, disparity
        else:
            disp_to_calc = ((disparity.astype(np.float32)/16-MinDisp)/NumDisp)
            return disparity_color, disparity_color, disparity_grayscale, disp_to_calc, disparity