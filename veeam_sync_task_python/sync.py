# time provides various time-related functions
# shutil module offers a number of high-level operations on files and collections of files
# os provides a portable way of using operating system dependent functionality.
# filecmp defines functions to compare files and directories, with various optional time/correctness trade-offs
# Only replicate from source -> replica (paths defined by user)
# Sync periodically (period defined by user)
# Log changes (log file path defined by user)
# Import packages needed
import time
import os
import filecmp
import shutil
import logging
import sched


def delete_leftover(cmp_obj):
    replica_path = cmp_obj.right
    # Get the files/directories that are ONLY in the REPLICA folder (old synced files to delete)
    path_array = cmp_obj.right_only

    if len(path_array) > 0:
        for x in path_array:
            delete_path = replica_path + "\\" + x

            # Condition to check if it is a file or a directory
            if not os.path.isfile(delete_path):
                shutil.rmtree(delete_path, ignore_errors=True)
            else:
                os.remove(delete_path)

            print("Deleted from the replica folder: ", delete_path)
            logger.debug("Deleted from the replica folder: %s", delete_path)

def copy_new(cmp_obj):
    s_path = cmp_obj.left
    r_path = cmp_obj.right
    # Get the files/directories that are ONLY in the SOURCE folder (new files/folders to sync)
    path_array = cmp_obj.left_only

    if len(path_array) > 0:
        for x in path_array:
            copy_source_path = s_path + "\\" + x
            full_replica_path = r_path + "\\" + x

            # If its a file -> copy it
            if os.path.isfile(copy_source_path):
                shutil.copy2(copy_source_path, r_path)
                print("Created a file copy from [",copy_source_path,"] in [", full_replica_path,"]")
                logger.debug("Created a file copy from [%s] in [%s]", copy_source_path,full_replica_path)
            # If its a directory, and it exists, delete it
            elif os.path.isdir(copy_source_path) and os.path.exists(copy_source_path):
                # Just to be sure?
                if(os.path.exists(full_replica_path)):
                    os.remove(full_replica_path)

                # Copy the whole folder tree
                # maybe use copy 2 to copy the folder and
                shutil.copytree(copy_source_path, full_replica_path)
                print("Copied the directory from [",copy_source_path,"] in [",full_replica_path,"]")
                logger.debug("Copied the directory from [%s] in [%s]", copy_source_path,full_replica_path)

def check_difs(cmp_obj):
    # Get all the differences at the current tree level
    diffs = cmp_obj.diff_files
    sub_dirs = cmp_obj.subdirs
    s_path = cmp_obj.left
    r_path = cmp_obj.right

    delete_leftover(cmp_obj)
    copy_new(cmp_obj)

    # If there are differences at this level OR sub folders to check
    if len(diffs)>0 or len(sub_dirs)>0:
        # Go through all the differences caught in files
        for name in diffs:
            copy_source_path = s_path + "\\" + name

            # Update the replica
            shutil.copy2(copy_source_path, r_path)
            print("Synced file in [",r_path,"\\",name,"]")
            logger.debug("Synced file in [%s\\%s]", r_path,name)

        # Go through all the sub folders and check their differences
        for sub_dcmp in sub_dirs.values():
            check_difs(sub_dcmp)

def sync_dirs(s_path, r_path):
    # Get the comparison object
    dir_compare = filecmp.dircmp(s_path, r_path)

    check_difs(dir_compare)

while True:
    source_path = input("Please enter the source folder full path: ")
    source_exists = os.path.isdir(source_path)

    if not source_exists:
        print("Please enter a valid folder.")
        continue
    else:
        break

while True:
    replica_path = input("Please enter the replica folder full path: ")
    replica_exists = os.path.isdir(replica_path)

    if not replica_exists:
        print("Please enter a valid folder.")
        continue
    else:
        break

while True:
    log_file_path = input("Please enter where you want the log file to be saved to: ")
    log_file_path_exists = os.path.isdir(log_file_path)

    if not log_file_path_exists:
        print("Please enter a valid path.")
        continue
    else:
        log_file_path = os.path.join(log_file_path + "\\folder_sync.log")
        # Access logging functionality
        logger = logging.getLogger(__name__)
        # Set logging level to debug
        logger.setLevel(logging.DEBUG)
        # Start the log file. Going to overwrite if there is already a log file
        logging.basicConfig(filename=log_file_path, encoding='utf-8', filemode='w', level=logging.DEBUG)
        break

while True:
    try:
        sync_interval = int(input("Please enter the synchronization interval in minutes: "))
    except ValueError:
        print("Please enter a valid interval in minutes")
        continue
    else:
        print("Synchronization interval of: ",sync_interval,"min")
        break

while(True):
    sync_dirs(source_path,replica_path)
    sync_interval_seconds = sync_interval * 60
    time.sleep(sync_interval_seconds)