import pyrealsense2 as rs
import os
import cv2
import numpy as np
import time
import matplotlib.pyplot as plt


# PARAMS
N_depth_smooth = 4
width  = 1280 #width of images
height = 720 #height of images
fps = 30 #framerate for acquisition
DS5_product_ids = ["0AD1", "0AD2", "0AD3", "0AD4", "0AD5", "0AF6", "0AFE", "0AFF", "0B00", "0B01", "0B03", "0B07","0B3A"] #available product ids
path_color='/home/cam_driver/Pictures/color/' #path to color folder
path_depth='/home/cam_driver/Pictures/depth/' #path to depth folder
path_smooth_depth='/home/cam_driver/Pictures/smooth_depth/' #path to smoothed depth folder
path_ir='/home/cam_driver/Pictures/ir/' #path to infrared folder
global_path='/home/cam_driver/Pictures/' #path to folders
set_emitter = 1 #activation of the infrared emittor for depth acquisition

# CHECK FOLDERS PATH
for path in [path_color,path_depth,path_ir]:
        if not os.path.isdir(path):
                os.mkdir(path)


# FUNCTION TO SMOOTH DEPTH FRAMES
def combine_frames(frame_list):
        dtype_in = frame_list[0].dtype
        X = np.array(frame_list,dtype=np.float32)
        X[X==0] = np.nan
        X = np.nanmean(X,axis=0)
        print(np.shape(X))
        X[X==np.nan] = 0
        return X.astype(dtype_in)
        
# FUNCTION TO VISUQLIWE LAST FRAME
def visu_depth(depth_map,label=""):
        X = depth_map.astype(np.float32)
        X[X==0] = np.nan
        plt.imshow(X,cmap='viridis')
        plt.axis('off')
        #plt.show()
        plt.savefig(f'{global_path}last_depth_colorized_{label}.png')
        

# FUNCTION TO CHECK CURRENT DEVICE REALSENSE CONNECTED TO PI
def check_device():
        ctx = rs.context()
        ds5_dev = rs.device()
        devices = ctx.query_devices()
        if len(devices)==0:
                raise Exception("No realsense device connected, acquisition impossible.")
        dev = devices[0]
        if dev.supports(rs.camera_info.product_id) and str(dev.get_info(rs.camera_info.product_id)) in DS5_product_ids:
                if dev.supports(rs.camera_info.name):
                        print("Found device that supports advanced mode :", dev.get_info(rs.camera_info.name))
        else : # no device supporting advanced mode, raise excpetion
                raise Exception("No device that supports advanced mode was found")
        # GET ADVANCE MODE
        advnc_mode = rs.rs400_advanced_mode(dev)
        print("Advanced mode is", "enabled" if advnc_mode.is_enabled() else "disabled")


# LAUNCH ACQUISITION
def launch_acquisition(date_string):

        try :
                # CREATE PIPELINE
                pipeline = rs.pipeline()

                #Create a config and configure the pipeline to stream
                #  different resolutions of color and depth streams
                config = rs.config()
                config.enable_stream(rs.stream.depth, width, height, rs.format.z16, fps)
                config.enable_stream(rs.stream.color, width, height, rs.format.bgr8, fps) #bgr to adapt to cv2 format
                config.enable_stream(rs.stream.infrared,1, width, height, rs.format.y8, fps)
                config.enable_stream(rs.stream.infrared,2, width, height, rs.format.y8, fps)
                
                # START PIPELINE
                profile = pipeline.start(config)
            
        except Exception as acquisition_exception :
                raise acquisition_exception
                
        try :
                
                # start and configure pipeline
                device = profile.get_device()
                # configure emitters for depth frames
                depth_sensor = device.first_depth_sensor()
                depth_sensor.set_option(rs.option.emitter_enabled, set_emitter)
                # check emitter availability
                emitter = depth_sensor.get_option(rs.option.emitter_enabled)
                if emitter==1:
                    print('Emitter is activated')
                else:
                    print('Emitter is desactivated')
                # align on color frame
                align = rs.align(rs.stream.color)
                # colorize depth frames
                colorizer = rs.colorizer()
                # get frames
                time.sleep(5) # take care of exposure time
                #align_depth_colorized = []
                align_depth = []
                for i in range(N_depth_smooth):
                        frames = pipeline.wait_for_frames()
                        aligned_frames = align.process(frames)
                        if i==0:
                                align_color = np.asanyarray(aligned_frames.get_color_frame().get_data())
                                align_ir = np.asanyarray(aligned_frames.get_infrared_frame(1).get_data())
                        align_depth.append(np.asanyarray(aligned_frames.get_depth_frame().get_data()))
                # save images
                cv2.imwrite(path_color+'color_'+date_string+'.png',align_color)
                cv2.imwrite(path_ir+'ir_'+date_string+'.png',align_ir)
                cv2.imwrite(path_depth+'depth_'+date_string+'.png',align_depth[0])
                smooth_depth = combine_frames(align_depth)
                cv2.imwrite(path_smooth_depth+'sdepth_'+date_string+'.png',smooth_depth)
                visu_depth(align_depth[0])
                visu_depth(smooth_depth,"smooth")
            
        except Exception as acquisition_exception :
                raise acquisition_exception

        finally  :
                pipeline.stop()
