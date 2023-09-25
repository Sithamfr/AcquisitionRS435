"""
MAIN CODE FOR ACQUISITION WITH REALSENSE
"""

from datetime import datetime

# GET DATETIME
date_now = datetime.now()

# GET PREVIOUS ACQUISITION STATUS
try :   
    # read file
    with open('last_acquisition_status','r') as f:
        status = f.readlines()
except :
    # create file if doesn't exist
    open('last_acquisition_status','w').close()
    status = ['1']

# LAUNCH ACQUISITION
try :
    import acquisition_management
    date_string_file = date_now.strftime("%Y-%m-%d_%H-%M")
    acquisition_management.check_device()
    acquisition_management.launch_acquisition(date_string_file)
    with open('last_acquisition_status','w') as f:
        f.write("1")
except Exception as e :
    # restart usb port and try again
    try :
        import reset_usb_port_cam
        import acquisition_management
        date_string_file = date_now.strftime("%Y-%m-%d_%H-%M")
        acquisition_management.check_device()
        acquisition_management.launch_acquisition(date_string_file)
        with open('last_acquisition_status','w') as f:
            f.write("1")
    except Exception as e:
        # send alert if necessary
        import alert_management
        date_string_alert = date_now.strftime("%d/%m/%Y at %H:%M:%S")
        first_time_error = alert_management.send_alert(e,status,date_string_alert)
        if not first_time_error:
            alert_management.reboot_pi(10)
finally :
    print("Done")
