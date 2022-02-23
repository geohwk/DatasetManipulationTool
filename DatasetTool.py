#!/usr/bin/python 
from tkinter import Image
import PySimpleGUI as sg
import os
import cv2
import glob 
import shutil
from enum import Enum

window = None
values = None

slider_ratio = 0.5

Images_In_Dir = 0
train_input_dir = None
val_input_dir = None

Execute = False

datasetFormat = False

MainMenu = Enum('MainMenu', 'extraction reduce increase create nothing')
SideMenu = Enum('SideMenu', 'random smallest largest nothing')

MainMenuState = MainMenu.nothing
SideMenuState = SideMenu.nothing

dataset_multiplier = 1

im_in_train = 0
im_in_val = 0

input_folder = None
output_folder = None

sg.theme("DarkBlue")
sg.set_options(font=("Courier New", 16))

#-----------------------State Handlers-------------------------------
def Main_Menu_State():
    global MainMenuState
    if MainMenuState == MainMenu.extraction:
        print("Extract Bounding Boxes Selection")
        window['reduce_set'].update(False)
        window['increase_set'].update(False)
        window['create_set'].update(False)
        FP_Extraction_Menu()
    elif MainMenuState == MainMenu.reduce:
        print("Reduce Set Selection")
        window['fp_extraction'].update(False)
        window['increase_set'].update(False)
        window['create_set'].update(False)
        Reduce_Set_Menu()
    elif MainMenuState == MainMenu.increase:
        print("Increase Set Selection")
        window['reduce_set'].update(False)
        window['fp_extraction'].update(False)
        window['create_set'].update(False)
        Increase_Set_Menu()
    elif MainMenuState == MainMenu.create:
        print("Create Set Selection")
        window['reduce_set'].update(False)
        window['fp_extraction'].update(False)
        window['increase_set'].update(False)
        Create_Set_Menu()
    else:
        print("No Selection...")

def Side_Menu_State():
    global SideMenuState
    if SideMenuState == SideMenu.random:
        window['smallest_reduce'].update(False)
        window['largest_reduce'].update(False)
    elif SideMenuState == SideMenu.largest:
        window['smallest_reduce'].update(False)
        window['random_reduce'].update(False)
    elif SideMenuState == SideMenu.smallest:
        window['random_reduce'].update(False)
        window['largest_reduce'].update(False)
    else:
        pass


def Directory_Stats_Selection():
    global datasetFormat, im_in_train, im_in_val, Images_In_Dir, dataset_multiplier, slider_ratio
    if(datasetFormat == True):
        print("Dataset Format")
        window['im_in_dir'].update('Images in Train Folder: ' + str(int(im_in_train)) + ', Val Folder: '+ str(im_in_val))
        window['im_in_dir'].update(visible=True)
        trainVal = float(im_in_train)*float(dataset_multiplier)
        valVal = float(im_in_val)*float(dataset_multiplier)
        window['im_in_out_dir'].update('Projected Images in Output Train Folder: ' + str(int(trainVal)) + ', Val Folder: '+ str(int(valVal)))
        window['im_in_out_dir'].update(visible=True)
    elif(datasetFormat == False) and MainMenuState != MainMenu.create:
        print("Image Folder Format")
        window['im_in_dir'].update('Images in Input Folder: ' + str(Images_In_Dir))
        window['im_in_dir'].update(visible=True)
        window['im_in_out_dir'].update('Projected Images in Output Folder: ' + str(int(Images_In_Dir*dataset_multiplier)))
        window['im_in_out_dir'].update(visible=True)
    elif(datasetFormat == False) and MainMenuState == MainMenu.create:
        window['im_in_dir'].update('Images in Input Folder: ' + str(Images_In_Dir))
        window['im_in_dir'].update(visible=True)
        trainVal = float(Images_In_Dir)*float(slider_ratio)
        valVal = float(Images_In_Dir)*float(1 - slider_ratio)
        window['im_in_out_dir'].update('Projected Images in Output Train Folder: ' + str(int(trainVal)) + ', Val Folder: '+ str(int(valVal)))
        window['im_in_out_dir'].update(visible=True)

#-----------------------Event Handlers-------------------------------
def Event_Handler():
    global MainMenuState, SideMenuState, output_folder, input_folder
    global values, datasetFormat, Images_In_Dir, im_in_train, im_in_val
    global dataset_multiplier, slider_ratio, Execute

    event, values = window.read()
    if event in (sg.WIN_CLOSED, 'Exit'):
        return False
    if event == '-INFOLDER-':
        im_in_train = 0
        im_in_val = 0
        input_folder = values['-INFOLDER-']
        if(Get_Dataset_Folders() == False):
            datasetFormat = False
        else:
            datasetFormat = True
        Images_In_Dir = len(os.listdir(input_folder))
        return True
    if event == '-OUTFOLDER-':
        output_folder = values['-OUTFOLDER-'] 
        return True
    if event == 'fp_extraction':
        dataset_multiplier = 1
        
        if(values['fp_extraction'] == 0):
            Clear_Menu()
            MainMenuState = MainMenu.nothing
        elif(Check_Folders_Selected() == False):
            print("No Folders")
            return True
        else:
            MainMenuState = MainMenu.extraction
            return True
    if event == 'reduce_set':
        dataset_multiplier = 1
        
        if(values['reduce_set'] == 0):
            Clear_Menu()
            MainMenuState = MainMenu.nothing
        elif(Check_Folders_Selected() == False):
            return True
        else:
            MainMenuState = MainMenu.reduce
            return True
    if event == 'increase_set':
        dataset_multiplier = 1
        if(values['increase_set'] == 0):
            Clear_Menu()
            MainMenuState = MainMenu.nothing
        elif(Check_Folders_Selected() == False):
            return True
        else:
            MainMenuState = MainMenu.increase
            return True
    if event == 'create_set':
        dataset_multiplier = 1
        if(values['create_set'] == 0):
            Clear_Menu()
            MainMenuState = MainMenu.nothing
        elif(Check_Folders_Selected() == False):
            return True
        else:
            MainMenuState = MainMenu.create
            return True
    if event == 'random_reduce':
        SideMenuState = SideMenu.random

    if event == 'smallest_reduce':
        SideMenuState = SideMenu.smallest

    if event == 'largest_reduce':
        SideMenuState = SideMenu.largest

    if event == 'execute':
        if(Check_Folders_Selected() == True) and (Check_Box_Selected() == True):
            if(MainMenuState == MainMenu.reduce):
                if(Sub_Check_Box_Selected() == True):
                    Execute = True
            else:
                Execute = True
         
    if event == 'folder_multiplier' + '_Enter':
        dataset_multiplier = float(values['folder_multiplier'])

    if event == 'submit_button':
        newDirectory = output_folder + "/" + values['new_folder_text']
        os.mkdir(newDirectory)
        output_folder = newDirectory

    if event == 'slider':
        slider_ratio = values['slider']

def Processes():
    global Execute
    if Execute == True:
        print("Execute = True")
        print("Running Selection")
        global MainMenuState
        if MainMenuState == MainMenu.extraction:
            FP_Extraction(input_folder, output_folder)
        elif MainMenuState == MainMenu.reduce:
            print("Reduce")
            Reduce_Set()
        elif MainMenuState == MainMenu.increase:
            Increase_Set()
        elif MainMenuState == MainMenu.create:
            Create_Set()
        else:
            print("No Selection...")
        Execute = False
    else:
        pass

#-----------------------Layout-------------------------------
def Layout_Setup():
    global window
    left_col_layout = [
    [sg.Text('Input Folder:'), sg.In(size=(25,1), enable_events=True, key='-INFOLDER-'), sg.FolderBrowse()],
    [sg.Checkbox(' - Bounding Box Extraction', default=False, enable_events=True, key="fp_extraction")],
    [sg.Checkbox(' - Reduce Set Size', default=False, enable_events=True, key="reduce_set")],
    [sg.Checkbox(' - Increase Set Size', default=False, enable_events=True, key="increase_set")],
    [sg.Checkbox(' - Create train/val Dataset from Images', default=False, enable_events=True, key="create_set")]
    
    ]
    right_col_layout = [
        [sg.Text('Output Folder:'), sg.In(size=(25,1), enable_events=True ,key='-OUTFOLDER-'), sg.FolderBrowse()],
        [sg.Text('Create New Folder in Output Folder:'),sg.InputText(size=(15,1), key="new_folder_text"),sg.Button('Submit',key="submit_button", enable_events=True)],
        [sg.Text('Images in Folder', visible=True, key="im_in_dir")], 
        [sg.Text('Images in Folder', visible=True, key="im_in_out_dir")],
        [sg.Slider(range=(0,1),default_value=0.5,size=(30,10),orientation='horizontal',visible=True, key='slider', font=("Courier New", 10), enable_events=True, resolution=.1)],
        [sg.Text('Dataset Multiplier:', key='folder_multiplier_text', visible=True)], 
        [sg.Input(str(dataset_multiplier), size=(10,1), key='folder_multiplier', visible=True)],
        [sg.Checkbox(' - Random', default=False, enable_events=True, visible=True, pad=(86, 0), key="random_reduce")],
        [sg.Checkbox(' - Remove Smallest', default=False, enable_events=True, visible=True, key="smallest_reduce")],
        [sg.Checkbox(' - Remove Largest', default=False, enable_events=True, visible=True, pad=(14, 0), key="largest_reduce")],
        [sg.Button('Execute', enable_events=True, key="execute")],
        [sg.ProgressBar(max_value = 1000, orientation='horizontal', size=(65, 10), key="progress_bar", visible = True)]
    ]

    layout =[
        [sg.Column(left_col_layout, element_justification='left', expand_x=True, vertical_alignment='t'),
        sg.Column(right_col_layout, element_justification='right', expand_x=True, vertical_alignment='t')]
    ]

    window = sg.Window('Dataset Manipulation Tool', layout,resizable=True, finalize=True,size=(1100, 360), location=(500, 400))
    window['folder_multiplier'].bind("<Return>", "_Enter")  


#----------------------------------Check Functions------------------------------------------

def Check_Folders_Selected():
    global input_folder
    global output_folder
    global window
    if((input_folder == None) or (output_folder == None)):
        sg.Popup('Select Input and Output Folders', keep_on_top=True, location=(960, 540))
        window['fp_extraction'].update(False)
        window['increase_set'].update(False)
        window['reduce_set'].update(False)
        window['create_set'].update(False)
        return False
    else:
        return True

def Check_Box_Selected():
    if(values['fp_extraction'] + values['increase_set'] + values['reduce_set'] + values['create_set']) != 1:
        sg.Popup('Select Tool Option', keep_on_top=True, location=(960, 540))
        return False
    else:
        return True

def Sub_Check_Box_Selected():
    if(values['random_reduce'] + values['smallest_reduce'] + values['largest_reduce']== 0):
        sg.Popup('Please Select Reduce Option', keep_on_top=True, location=(960, 540))
        return False
    else:
        return True

#----------------------------------Menu Functions---------------------------------------

def Get_Dataset_Folders():
    global train_input_dir
    global val_input_dir
    global im_in_train
    global im_in_val
    flag = 0
    for file in os.listdir(input_folder):
        if(file == "train"):
            train_input_dir = input_folder + "/" + file
            flag = 1
        elif(file == "val"):
            val_input_dir = input_folder + "/" + file
            flag = 1

    if(flag == 0):
        sg.Popup('WARNING: No Train/Val folders in input', keep_on_top=True, location=(960, 540))
        return False
    im_in_train = len(os.listdir(train_input_dir + "/Battery")) + len(os.listdir(train_input_dir + "/FP"))
    im_in_val = len(os.listdir(val_input_dir + "/Battery")) + len(os.listdir(val_input_dir + "/FP"))
    return True

def Reduce_Set_Menu():
    Clear_Menu()
    Directory_Stats_Selection()

    window['folder_multiplier_text'].update("Dataset Multiplier (< 1):")
    window['folder_multiplier_text'].update(visible=True)
    window['folder_multiplier'].update(dataset_multiplier)
    window['folder_multiplier'].update(visible=True)
    window['random_reduce'].update(visible=True)
    window['smallest_reduce'].update(visible=True)
    window['largest_reduce'].update(visible=True)

def Increase_Set_Menu():
    Clear_Menu()
    Directory_Stats_Selection()

    window['folder_multiplier_text'].update("Dataset Multiplier (x2, x3, x4):")
    window['folder_multiplier_text'].update(visible=True)
    window['folder_multiplier'].update(round(dataset_multiplier,0))
    window['folder_multiplier'].update(visible=True)

def FP_Extraction_Menu():
    Clear_Menu()
    Directory_Stats_Selection()
    window['im_in_out_dir'].update(visible=False)
    if(datasetFormat == True):
        sg.Popup('WARNING: Image Folder is in Dataset Format', keep_on_top=True, location=(960, 540))

def Create_Set_Menu():
    Clear_Menu()
    Directory_Stats_Selection()
    window['slider'].update(visible=True)
    if(datasetFormat == True):
        sg.Popup('WARNING: Image Folder is in Dataset Format', keep_on_top=True, location=(960, 540))

def Clear_Menu():
    global dataset_multiplier
    global window
    window['slider'].update(visible=False)
    window['im_in_dir'].update(visible=False)
    window['im_in_out_dir'].update(visible=False)
    window['random_reduce'].update(visible=False)
    window['smallest_reduce'].update(visible=False)
    window['largest_reduce'].update(visible=False)
    window['folder_multiplier_text'].update(visible=False)
    window['folder_multiplier'].update(visible=False)
    window['progress_bar'].update(0)
    #window['folder_multiplier'].update(str(round(dataset_multiplier, 1)))

#--------------------------Process Functions-----------------------------------

def FP_Extraction(input_folder, output_folder):
    window['progress_bar'].update(0)
    window['progress_bar'].update(visible=True)
    count = 0
    for file in os.listdir(input_folder):
        image = cv2.imread(input_folder +"/"+ str(file))
        betweenDots = str(file).split('.')
        betweenUnderscores = str(betweenDots[1]).split('_')
        x1 = betweenUnderscores[1]
        y1 = betweenUnderscores[2]
        x2 = betweenUnderscores[3]
        y2 = betweenUnderscores[4]
        cropImage(x1, y1, x2, y2, image, output_folder, file)
        count = count + 1
        window['progress_bar'].update(1000*(count/len(os.listdir(input_folder))))
    window['progress_bar'].update(0)
    #window['progress_bar'].update(visible=False)

def cropImage(x1, y1, x2, y2, image, output_folder, file):

    roi = image[int(y1):int(y2), int(x1):int(x2)]
    cv2.imwrite(output_folder +"/"+ str(file), cv2.resize(roi, (299, 299)))

def Create_Dataset_Folder():
    folder = "/train"
    for i in range(0, 2):
        try:
            os.mkdir(output_folder + folder)
        except:
            print("Folder Already Exists...")
        try:
            os.mkdir(output_folder + folder + "/Battery")
        except:
            print("Folder Already Exists...")
        try:
            os.mkdir(output_folder + folder + "/FP")
        except:
            print("Folder Already Exists...")
        folder = "/val"

def Generate_Rotations(file, folder):
    fileImage = cv2.imread(input_folder + folder + str(file))
    cv2.imwrite(output_folder + folder + str(file), fileImage)
    
    if(dataset_multiplier >= 2):
        image90 = cv2.rotate(fileImage, cv2.ROTATE_90_CLOCKWISE)
        cv2.imwrite(output_folder + folder + "90-" + str(file), image90)
        if(dataset_multiplier >= 3):
            image180 = cv2.rotate(fileImage, cv2.ROTATE_180)
            cv2.imwrite(output_folder + folder + "180-" + str(file), image180)
            if(dataset_multiplier >= 4):
                image270 = cv2.rotate(fileImage, cv2.ROTATE_90_COUNTERCLOCKWISE)
                cv2.imwrite(output_folder + folder +  "270-" + str(file), image270)

def Sort_And_Move(folder, count):

      # Get a list of files (file paths) in the given directory 
    list_of_files = filter( os.path.isfile,
                        glob.glob(input_folder + folder + '*') )

    if(values['random_reduce'] == 1):
        list_of_files = sorted( list_of_files,
                            key =  lambda x: os.stat(x).st_mtime)
    else:
        list_of_files = sorted( list_of_files,
                            key =  lambda x: os.stat(x).st_size)
    
    #TODO: Sort this mess
    # Sort list of files in directory by size 
    
    if(values['smallest_reduce'] == 1):
        list_of_files.reverse()
    
    original_length = len(list_of_files)
    for i, file in enumerate(list_of_files):
        count = count + 1
        window['progress_bar'].update(1000*(count/((im_in_train + im_in_val)*(dataset_multiplier))))
        if(float(i/original_length) > float(dataset_multiplier)):
            break
        else:
            shutil.copy(file, output_folder + folder)
    return count

def Reduce_Set():
    window['progress_bar'].update(visible = True)
    count = 0
    Create_Dataset_Folder()
    folder = "/train/Battery/"
    count = Sort_And_Move(folder, count)
    folder = "/train/FP/"
    count = Sort_And_Move(folder, count)
    folder = "/val/Battery/"
    count = Sort_And_Move(folder, count)
    folder = "/val/FP/"
    Sort_And_Move(folder, count)
    window['progress_bar'].update(0)
    #window['progress_bar'].update(visible = False)

def Increase_Set():
    if(im_in_train == 0):
        dataset = os.listdir(input_folder)
        for i, file in enumerate(dataset):
            Generate_Rotations(file, "/")
            
            window['progress_bar'].update(1000*(i/(len(dataset))))
        window['progress_bar'].update(0)
        return
    Create_Dataset_Folder()
    dataset = os.listdir(input_folder)
    folder = "/train/Battery/"
    window['progress_bar'].update(visible=True)
    count = 0
    for i, file in enumerate(os.listdir(input_folder + folder)):
        Generate_Rotations(file, folder)
        count = count + 1
        window['progress_bar'].update(1000*(count/(im_in_train + im_in_val)))

    folder = "/train/FP/"
    for i, file in enumerate(os.listdir(input_folder + folder)):
        Generate_Rotations(file, folder)
        count = count + 1
        window['progress_bar'].update(1000*(count/(im_in_train + im_in_val)))

    folder = "/val/Battery/"
    for i, file in enumerate(os.listdir(input_folder + folder)):
        Generate_Rotations(file, folder)
        count = count + 1
        window['progress_bar'].update(1000*(count/(im_in_train + im_in_val)))
    folder = "/val/FP/"
    for i, file in enumerate(os.listdir(input_folder + folder)):
        Generate_Rotations(file, folder)
        count = count + 1
        window['progress_bar'].update(1000*(count/(im_in_train + im_in_val)))
    window['progress_bar'].update(0)
    #window['progress_bar'].update(visible=False)
    
def Create_Set():
    pass

#-----------------------Main-------------------------------

def main():
    print("Dataset Manipulation Tool Startup...")
    print("Defining Layout...")
    Layout_Setup()
    Clear_Menu()
    print("Running...")
    while(True):
        if(Event_Handler() == False):
            break
        Main_Menu_State()
        Side_Menu_State()
        Processes()

if __name__== "__main__" :
        main()

