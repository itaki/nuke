import subprocess
drive_path = '/Volumes/Mercury'
#drive_path = '/Volumes/Dettifoss2'
def is_network_drive(drive_path):
    try:
        output = subprocess.check_output(['df', '-t', drive_path])
        print (f"Output : {output}")
        lines = output.decode().split('\n')[1:]
        for line in lines:
            if line:
                drive_info = line.split()
                drive_type = drive_info[0]
                print (f"Drive Type : {drive_type}")
                if 'smb' in drive_type:
                    print (f"Requested Cache Drive : {drive_path} is a network drive. Please use a local drive for cache.")
                    return True
        print (f"Requested Cache Drive : {drive_path} is a local drive.")
        return False
    except subprocess.CalledProcessError:
        return False

print ( is_network_drive(drive_path) )

