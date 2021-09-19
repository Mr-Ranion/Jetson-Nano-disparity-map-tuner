import PIL
from tkinter import*
from PIL import Image,ImageTk
from child_window import ChildWindow
from stereo_frame import Stereo_Jet
import json

class Window:
    Settings = []
    child_root = 0
    settings_window = 0
    SW_IsOpen = False
    Button_active = ACTIVE
    stereo = 0
    def __init__(self, width, height, title="Jetson Stereo", resizable=(False, False),icon=None):
        self.root = Tk()
        self.root.title(title)
        self.root.geometry(f"{width}x{height}")
        self.root.resizable(resizable[0],resizable[1])
    
        if icon:
           self.root.iconbitmap(icon)
    
    def draw_menu(self):
        menu_bar = Menu(self.root)
        self.root.configure(menu=menu_bar)

    def run(self):
        self.root.mainloop()
    
    def create_settings_window(self, width, height, title="Child", resizable=(False,False), icon=None):
        settings_window = ChildWindow(self.root,
                                           width,
                                           height, 
                                           title, 
                                           resizable, 
                                           icon)
        settings_window.draw_widgets(self)
        settings_window.load_dm_settings()
        return settings_window

    def open_child_window(self):
        self.settings_window = self.create_settings_window(465,475,"Settings")
        self.SW_IsOpen = self.settings_window.IsOpen
        self.child_root = self.settings_window.root
        self.Button_active = DISABLED
        self.draw_buttons()

    def load_saved_settings(self):

        fName = 'depth_map_settings.txt'
        #print('Loading parameters from file...')
        f=open(fName, 'r')
        data = json.load(f)

        set1 = int(data['preFilterSize'])
        set2 = int(data['preFilterCap'])
        set3 = int(data['minDisparity'])
        set4 = int(data['numberOfDisparities'])
        set5 = int(data['textureThreshold'])
        set6 = int(data['uniquenessRatio'])
        set7 = int(data['speckleRange'])
        set8 = int(data['speckleWindowSize'])
        set9 = int(data['BF_pix_diameter'])
        set10 = int(data['BF_sigmaColor'])
        set11 = int(data['BF_sigmaSpace'])
        set12 = int(data['WLS_lmbda'])
        set13 = float(data['WLS_sigma'])
        set14 = int(data['WLS_DDR'])
        set15 = int(data['WLS_LRS'])

        self.Settings = [set1,set2,set3,set4,set5,set6,set7,set8,set9,set10,set11,set12,set13,set14,set15]
       
        f.close()
        return self.Settings 
    
    def destroy_settings_window(self):
        self.SW_IsOpen = False
        self.Button_active = ACTIVE
        self.child_root.destroy()
        self.draw_buttons() 
        
    def chek_settings_window(self):
        if (self.SW_IsOpen == True):
            self.child_root.protocol("WM_DELETE_WINDOW",self.destroy_settings_window)
        else:
            pass
        
    def get_settings(self):
        if (self.SW_IsOpen == True):
            self.Settings = self.settings_window.get_scale_settings()
        else:
            self.Settings = self.load_saved_settings()
        #print(self.Settings)

    def DM_video_cap(self):
        Rectified_images = LabelFrame(self.root, width=640, height=240, text = "Left and Right rectified videiocap")
        Rectified_images.grid(row=0,column=0,padx=10,pady=10)
        DM_WLS_frame = LabelFrame(self.root,width=640,height=240,text="Disparity map and WLS filtered map")
        DM_WLS_frame.grid(row=1,column=0)

        label1 = self.draw_label(grid_in=Rectified_images,row=0,column=0)
        label2 = self.draw_label(grid_in=Rectified_images,row=0,column=1)
        label3 = self.draw_label(grid_in=DM_WLS_frame,row=1,column=0)
        label4 = self.draw_label(grid_in=DM_WLS_frame,row=1,column=1)
        self.stereo = Stereo_Jet()
        self.stereo.system_command()
        cam1,cam2 = self.stereo.camera_set(use_csi=True,
                                           use_usb=False,
                                           width=320,
                                           height=240,
                                           scale_ratio=1)

        LMX,LMY,RMX,RMY,LProg,Rprog = self.stereo.load_calib_settings(240)
        def video_cap():
            self.chek_settings_window()
            self.get_settings()
            settings = self.Settings
            ret1,ret2,img1,img2 = self.stereo.camera_read(cam1,cam2)
            if (ret1 == True) & (ret2 == True):
                rectified_pair,imgRcut,imgLcut=self.stereo.GPU_Remap_frame(img1,
                                                                           img2,
                                                                           LMX,
                                                                           LMY,
                                                                           RMX,
                                                                           RMY)
                Filt_D,Color_D,Gray_D,Calc_D,D=self.stereo.stereo_depth_map(rectified_pair,
                                                                            dm_colors_autotune=True,
                                                                            use_wls_filt=True,
                                                                            settings=settings)
            self.update_label(label=label1,image_arr=imgLcut)
            self.update_label(label=label2,image_arr=imgRcut)
            self.update_label(label=label3,image_arr=Color_D)
            self.update_label(label=label4,image_arr=Filt_D)
            self.root.after(1,video_cap)
        video_cap()

    def draw_buttons(self): 
        Button_frame = LabelFrame(self.root,width=640,height=50)
        Button_frame.grid(row=2,column=0,pady=10)
        B1 = Button(self.root, 
                    text = "Settings",
                    command = self.open_child_window,
                    state = self.Button_active)
        B1.grid(in_= Button_frame,row=0,column=0)
        
    def draw_label(self,grid_in,row,column,width=320,height=240):
        label = Label(self.root,width=width,height=height)
        label.grid(in_= grid_in,row=row,column=column)
        return label

    def update_label(self,label,image_arr):
        image = Image.fromarray(image_arr)
        PhIm = ImageTk.PhotoImage(image)
        label.configure(image=PhIm)
        label.image = PhIm

if __name__ == "__main__":
    window = Window(670,600, "Jetson Stereo Tuner")
    window.draw_buttons()
    window.DM_video_cap()
    window.run()