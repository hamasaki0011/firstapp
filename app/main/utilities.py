# 2023.11.15 Show disk capacity
import shutil

def disk_chk():
    disk_total, disk_used, disk_free = shutil.disk_usage('./')
    
    total = f'総容量: {int(disk_total / (2**30))} GiB'
    used = f'使用済み: {int(disk_used / (2**30))} GiB'
    free = f'空き容量: {int(disk_free / (2**30))} GiB'
    
    return (total, used, free)