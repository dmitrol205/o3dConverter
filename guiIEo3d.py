from o3dConvX import O3dConvX
from o3dConvWaveFront import O3dConvWaveFront
import tkinter as tk
from tkinter import BooleanVar, Entry, StringVar, filedialog as fd
from tkinter.constants import DISABLED, HORIZONTAL, NORMAL
from o3dModel import  Model
import os

# create the root window
root = tk.Tk()
root.title('O3d converter')
root.resizable(False, False)
root.geometry('640x480')
obj=None

version=tk.Scale(root,from_=1,to=7,orient=HORIZONTAL)
version.grid(row=1,column=2)
version['state']=DISABLED
f1v=BooleanVar()
f1=tk.Checkbutton(root,text="dword/word Faces",variable=f1v)
f1['state']=DISABLED
f1.grid(row=2,column=2)
f2v=BooleanVar()
f2=tk.Checkbutton(root,text="idk",variable=f2v)
f2['state']=DISABLED
f2.grid(row=3,column=2)
def keych(_):
    keyds.set(str(key.get()))
key=tk.Scale(root,from_=0,to=4294967295,orient=HORIZONTAL,command=keych)
key.grid(row=4,column=2)
key['state']=DISABLED
keyds=StringVar()
def cbk(_1,_2,_3):
    try:
        val=int(keyds.get())
    except ValueError:
        val=-1
    if 0<=val and val<=4294967295:
        if key.get()!=val:
            key.set(val)
        return True
    else:
        keyds.set(str(key.get()))
        return False
    
keyds.trace_add('write',cbk)
keyd=tk.Entry(root,textvariable=keyds)
keyd.grid(row=4,column=3)
keyd['state']=DISABLED

def update_values():
    version['state']=NORMAL
    f1['state']=NORMAL
    f2['state']=NORMAL
    key['state']=NORMAL
    keyd['state']=NORMAL
    version.set(obj.version)
    f1v.set(obj.f1)        
    f2v.set(obj.f2)        
    key.set(obj.udata)

def sv_file():
    filetypes = (
        ('O3d models', '*.o3d'),
    )

    filename = fd.asksaveasfilename(
        title='Save to file',
        initialdir=r'D:\Program Files (x86)\OMSI 2.2.027\Vehicles\debug',
        filetypes=filetypes)
    if filename!="":
        fex=os.path.splitext(filename)
        if fex[1]!='.o3d':
            filename=fex[0]+'.o3d'
        if obj!=None:
            obj.writeTo(filename,version.get(),f1v.get(),f2v.get(),int(keyds.get()))
            update_values()
            print("Saved to "+filename)
        else:
            print("You have not loaded any model")
        


def select_file():
    global obj
    filetypes = (
        ('O3d models', '*.o3d'),
    )

    filename = fd.askopenfilename(
        title='Open a file',
        initialdir=r'D:\Program Files (x86)\OMSI 2.2.027\Vehicles\debug',
        filetypes=filetypes)
    if filename!="":
        obj=Model(filename)
        update_values()

def import_f():
    global obj
    filetypes = (
        ('DirectX Ascii Frame', '*.x'),
    )

    filename = fd.askopenfilename(
        title='Open a file',
        initialdir=r'D:\Program Files (x86)\OMSI 2.2.027\Vehicles\debug',
        filetypes=filetypes)
    if filename!="":
        obj=O3dConvX()
        if obj.importDirectXAsciiFrame(filename):
            update_values()
            print("Imported from "+filename)
        else:
            print("import failed")

def import_wf():
    global obj
    filetypes = (
        ('WaveFront', '*.obj'),
    )

    filename = fd.askopenfilename(
        title='Open a file',
        initialdir=r'D:\Program Files (x86)\OMSI 2.2.027\Vehicles\debug',
        filetypes=filetypes)
    if filename!="":
        obj=O3dConvWaveFront()
        if obj.importWaveFront(filename):
            update_values()
            print("Imported from "+filename)
        else:
            print("import failed")
        

def export_f():
    filetypes = (
        ('DirectX Ascii Frame', '*.x'),
    )

    filename = fd.asksaveasfilename(
        title='Export to file',
        initialdir=r'D:\Program Files (x86)\OMSI 2.2.027\Vehicles\debug',
        filetypes=filetypes)
    if filename!="":
        fex=os.path.splitext(filename)
        if fex[1]!='.x':
            filename=fex[0]+'.x'
        if obj!=None:
            O3dConvX.transform(obj)
            obj.exportDirectXAsciiFrame(filename)
            print("Exported to "+filename)
        else:
            print("You have not loaded any model")

def export_wf():
    filetypes = (
        ('WaveFront', '*.obj'),
    )

    filename = fd.asksaveasfilename(
        title='Export to file',
        initialdir=r'D:\Program Files (x86)\OMSI 2.2.027\Vehicles\debug',
        filetypes=filetypes)
    if filename!="":
        fex=os.path.splitext(filename)
        if fex[1]!='.obj':
            filename=fex[0]+'.obj'
        if obj!=None:
            O3dConvWaveFront.transform(obj)
            obj.exportWaveFront(filename)
            print("Exported to "+filename)
        else:
            print("You have not loaded any model")

tk.Label(root,text="Version").grid(row=1,column=1)
tk.Label(root,text="Flag 1").grid(row=2,column=1)
tk.Label(root,text="Flag 2").grid(row=3,column=1)
tk.Label(root,text="Key").grid(row=4,column=1)
tk.Label(root,text="key==4294967295 or version<4 points mangle disabled").grid(row=5,columnspan=2,column=1)
tk.Label(root,text="tested key values 0 13887 4294967295").grid(row=6,columnspan=2,column=1)

# open button
open_button = tk.Button(
    root,
    text='Open *.o3d',
    command=select_file
)

open_button.grid(row=10,column=1)

save_button=tk.Button(
    root,
    text='Save *.o3d',
    command=sv_file
)
save_button.grid(row=10,column=3)

exp_button = tk.Button(
    root,
    text='To DirectX Ascii Frame',
    command=export_f
)
exp_button.grid(row=10,column=2)

imp_button = tk.Button(
    root,
    text='From DirectX Ascii Frame',
    command=import_f
)

imp_button.grid(row=10,column=4)

ewf_button = tk.Button(
    root,
    text='To WaveFront(.obj)',
    command=export_wf
)

ewf_button.grid(row=11,column=1)

iwf_button = tk.Button(
    root,
    text='From WaveFront(.obj)',
    command=import_wf
)

iwf_button.grid(row=11,column=2)

# run the application
root.mainloop()