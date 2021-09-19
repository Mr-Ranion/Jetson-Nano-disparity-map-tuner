from tkinter import*
import json
import numpy as np
import time

class ChildWindow:
   Settings = []
   MinDisp = 0
   NumDisp = 0
   UnRatio = 0
   Spcl_WS = 0
   Spcl_RG = 0
   Txtr_TH = 0
   BF_pixD = 0
   BF_SCol = 0
   BF_SSps = 0
   P_Flt_Cp = 0
   P_Flt_SZ = 0
   WLS_sigma = 0
   WLS_lmbda = 0
   WLS_DDR = 0
   WLS_LRS = 0
   IsOpen = False
   color = "#581845"

   def __init__(self, parent, width, height, title="Child Window", resizable=(False, False), icon=None):
       self.root = Toplevel(parent)
       self.root.title(title)
       self.root.geometry(f"{width}x{height}")
       self.root.resizable(resizable[0],resizable[1])
       self.IsOpen = True
       if icon:
          self.root.iconbitmap(icon)

   def call_child_root(self):
        return self.root
    
   def destroy_window(self):
        self.root.destroy()

   def destroy_settings_window(self):
        self.IsOpen = False
        self.root.destroy()

   def check_desrtoy_window(self):
        self.root.protocol("WM_DELETE_WINDOW",self.destroy_settings_window)
      
   def draw_scale(self,master,min,max,grid_in,length,row,column,name="Scale",start_pos=0,doublevar=False):
       if (doublevar == False):
             var = IntVar()
       else:
             var = DoubleVar()
       scale = Scale(self.root, 
                     label = name,
                     from_= min, 
                     to = max, 
                     orient = HORIZONTAL, 
                     variable = var, 
                     activebackground='#339999', 
                     length = length,
                     )
       scale.set(start_pos)
       scale.grid(in_= grid_in,row=row,column=column)
       return scale

   def get_scale_settings(self):
       
       set1 = self.P_Flt_SZ.get()
       set2 = self.P_Flt_Cp.get()
       set3 = self.MinDisp.get()
       set4 = self.NumDisp.get()
       set5 = self.Txtr_TH.get()
       set6 = self.UnRatio.get()
       set7 = self.Spcl_RG.get()
       set8 = self.Spcl_WS.get()
       set9 = self.BF_pixD.get()
       set10 = self.BF_SCol.get()
       set11 = self.BF_SSps.get()
       set12 = self.WLS_lmbda.get()
       set13 = self.WLS_sigma.get()
       set14 = self.WLS_DDR.get()
       set15 = self.WLS_LRS.get()
       self.Settings = [set1,set2,set3,set4,set5,set6,set7,set8,set9,set10,set11,set12,set13,set14,set15]
       return self.Settings
       

   def draw_scales(self):
        
        DM_settings_frame = LabelFrame(self.root,width=480, height=150, bg=self.color, text = "Disparity map settings")
        DM_settings_frame.grid(row=0,column=0)
        WLSF_settings_frame = LabelFrame(self.root,width=480, height=150, bg=self.color, text = "WLS filter settings")
        WLSF_settings_frame.grid(row=1,column=0)
        
        self.MinDisp = self.draw_scale(self,min=-100,max=100,grid_in=DM_settings_frame,row=0,column=0,length=150,name="MinDisparity")
        self.NumDisp = self.draw_scale(self,min= 16, max=256,grid_in=DM_settings_frame,row=0,column=1,length=150,name="NumDisparity")
        self.UnRatio = self.draw_scale(self,min = 1, max=20, grid_in=DM_settings_frame,row=0,column=2,length=150,name="Uniqueness_Ratio")
        
        self.Spcl_WS = self.draw_scale(self,min = 5, max=255,grid_in=DM_settings_frame,row=1,column=0,length=150,name="Speckle_Window_Size")
        self.Spcl_RG = self.draw_scale(self,min = 5, max=255,grid_in=DM_settings_frame,row=1,column=1,length=150,name="Speckle_Range")
        self.Txtr_TH = self.draw_scale(self,min = 0,max=1000,grid_in=DM_settings_frame,row=1,column=2,length=150,name="Texture_Threshold")
        
        self.P_Flt_Cp = self.draw_scale(self,min =2,max=63,grid_in=DM_settings_frame,row=2,column=0,length=150,name="Pre_Filter_Cap")
        self.P_Flt_SZ = self.draw_scale(self,min =5,max=255,grid_in=DM_settings_frame,row=2,column=1,length=150,name="Pre_Filter_Size")

        self.BF_pixD = self.draw_scale(self,min = 1,max=10, grid_in=WLSF_settings_frame,row=0,column=0,length=150,name="BF_pixel_diameter")
        self.BF_SCol = self.draw_scale(self,min =10,max=150,grid_in=WLSF_settings_frame,row=0,column=1,length=150,name="BF_sigma_color")
        self.BF_SSps = self.draw_scale(self,min =10,max=150,grid_in=WLSF_settings_frame,row=0,column=2,length=150,name="BF_sigma_space")

        self.WLS_sigma = self.draw_scale(self,min = 25,max=300, grid_in=WLSF_settings_frame,row=1,column=0,length=150,name="WLS_sigma_x100")
        self.WLS_lmbda = self.draw_scale(self,min = 800,max=80000,grid_in=WLSF_settings_frame,row=1,column=1,length=150,name="WLS_Lmbda")
        self.WLS_DDR = self.draw_scale(self,min =1,max=50,grid_in=WLSF_settings_frame,row=1,column=2,length=150,name="WLS_DRR")
        self.WLS_LRS = self.draw_scale(self,min =-50,max=50,grid_in=WLSF_settings_frame,row=2,column=0,length=150,name="WLS_LRS")
        
        
   
   def save_dm_settings(self):
        self.get_scale_settings()
        print('Saving to file...') 
        result = json.dumps({'preFilterSize':self.Settings[0], 'preFilterCap':self.Settings[1], \
                             'minDisparity':self.Settings[2], 'numberOfDisparities':self.Settings[3], 'textureThreshold':self.Settings[4], \
                             'uniquenessRatio':self.Settings[5], 'speckleRange':self.Settings[6], 'speckleWindowSize':self.Settings[7], \
                             'BF_pix_diameter':self.Settings[8], 'BF_sigmaColor':self.Settings[9], 'BF_sigmaSpace':self.Settings[10],\
                              'WLS_sigma':self.Settings[12], 'WLS_lmbda':self.Settings[11], 'WLS_DDR':self.Settings[13], 'WLS_LRS':self.Settings[14]},\
                              sort_keys=True, indent=4, separators=(',',':'))
        fName = 'depth_map_settings.txt'
        f = open (str(fName), 'w') 
        f.write(result)
        f.close()
        print ('Settings saved to file '+fName)
    
   def load_dm_settings(self): 
        fName = 'depth_map_settings.txt'
        print('Loading parameters from file...')
        f=open(fName, 'r')
        data = json.load(f)
        set1 = self.P_Flt_SZ.set(int(data['preFilterSize']))
        set2 = self.P_Flt_Cp.set(int(data['preFilterCap']))
        set3 = self.MinDisp.set(int(data['minDisparity']))
        set4 = self.NumDisp.set(int(data['numberOfDisparities']))
        set5 = self.Txtr_TH.set(int(data['textureThreshold']))
        set6 = self.UnRatio.set(int(data['uniquenessRatio']))
        set7 = self.Spcl_RG.set(int(data['speckleRange']))
        set8 = self.Spcl_WS.set(int(data['speckleWindowSize']))
        set9 = self.BF_pixD.set(int(data['BF_pix_diameter']))
        set10 = self.BF_SCol.set(int(data['BF_sigmaColor']))
        set11 = self.BF_SSps.set(int(data['BF_sigmaSpace']))
        set12 = self.WLS_lmbda.set(int(data['WLS_lmbda']))
        set13 = self.WLS_sigma.set(float(data['WLS_sigma']))
        set14 = self.WLS_DDR.set(int(data['WLS_DDR']))
        set15 = self.WLS_LRS.set(int(data['WLS_LRS']))

        self.Settings = [set1,set2,set3,set4,set5,set6,set7,set8,set9,set10,set11,set12,set13,set14,set15]
        f.close()
        return self.Settings   

   def draw_widgets(self,defalt):
        self.draw_scales()
        Buttons_frame = LabelFrame(self.root,width=480, height=150, bg=self.color)
        Buttons_frame.grid(row=2,column=0)
        Button(self.root, text="Save settings",command = self.save_dm_settings).grid(in_= Buttons_frame,row=1,column=1)
        Button(self.root, text="Load settings",command = self.load_dm_settings).grid(in_= Buttons_frame,row=2,column=1)
