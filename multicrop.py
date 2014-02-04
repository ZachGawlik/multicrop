'''
Select multiple image of same size that all need cropping in same area.
Select a region to crop on one image, and apply it to all selected images.
Saves cropped images with filename prefix 'Multicropped-'

Particularly useful for cropping the same area of many screenshots.
'''

from tkinter import filedialog
import tkinter as tk
from PIL import ImageTk, Image
import os


crop_coords = None
canvas_width = 400
canvas_height = 300


class StatusBar(tk.Frame):
    '''Instructional status bar along bottom.'''   
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.variable=tk.StringVar()        
        self.label=tk.Label(self, bd=1, relief=tk.SUNKEN, anchor=tk.W,
                            textvariable=self.variable,
                            font=('arial', 14, 'normal'))
        self.variable.set('Click Open.')
        self.label.pack(fill=tk.X)        
        self.pack(side=tk.BOTTOM, fill=tk.X)

    def update(self, newtext):
        self.variable.set(newtext)


class ButtonBar(tk.Frame):
    '''Container for all buttons.'''
    def __init__(self, master):
        tk.Frame.__init__(self, master)

        button = tk.Button(self, text='Open', command=self.openimage)
        button.pack(side=tk.LEFT)
        button_crop = tk.Button(self, text='Crop', command=self.crop)
        button_crop.pack(side=tk.LEFT)
        button_save = tk.Button(self, text='Save All', command=self.saveimages)
        button_save.pack(side=tk.LEFT)

        self.canvas = self.master.canvas
        self.imgfiles = None
        self.crops = []

        self.pack(side=tk.BOTTOM, fill=tk.X)

    def openimage(self):
        '''Select all images to crop. Display first to screen.'''
        try:
            self.master.statusbar.update('1. Select files to crop. '
                                         'Hold command to select multiple.')
            self.imgfiles = filedialog.askopenfilenames()
            imgfile = self.imgfiles[0]
            if imgfile and allimages(self.imgfiles):
                self.canvas.pil_img = Image.open(imgfile)
                self.setimage(self.canvas.pil_img)
                self.canvas.config(width=self.canvas.pil_img.size[0])
                self.canvas.config(height=self.canvas.pil_img.size[1])
                self.crops = []
                self.master.statusbar.update('2. Draw a region to crop.')
        except IOError:
            print('Files selected must be images')
            self.openimage()
        except:
            pass

    def setimage(self, img):
        '''Set canvas to display only the given image.'''
        self.canvas.img = ImageTk.PhotoImage(img)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.canvas.img) 
        region = (0, 0, self.canvas.img.width(), self.canvas.img.height())
        self.canvas.configure(scrollregion=region)

    def crop(self):
        '''Crop image on canvas according to created rectangle'''
        global crop_coords
        
        if crop_coords is None or not hasattr(self.canvas, 'pil_img'):
            return

        # order the rectangle's coordinates to be (left, top, right, bottom)
        ordered_coords = (
                min(crop_coords[0], crop_coords[2]),
                min(crop_coords[1], crop_coords[3]),
                max(crop_coords[0], crop_coords[2]),
                max(crop_coords[1], crop_coords[3]),
                )

        self.canvas.delete('rect')
        self.canvas.pil_img = self.canvas.pil_img.crop(ordered_coords)
        self.setimage(self.canvas.pil_img)

        self.canvas.config(width=ordered_coords[2]-ordered_coords[0])
        self.canvas.config(height=ordered_coords[3]-ordered_coords[1])
        self.crops.append(ordered_coords)
        crop_coords = None
        self.master.statusbar.update('All images cropped. Crop again or Save.')

    def applyall(self):
        '''Apply all crops to all selected image files.'''
        croppedimages = []
        newfilenames = []
        for imgfile in self.imgfiles:
            image = Image.open(imgfile)
            for cropping in self.crops:
                image = image.crop(cropping)
            croppedimages.append(image)
            newfilenames.append('/Multicropped-'.join(os.path.split(imgfile)))

        return croppedimages, newfilenames

    def saveimages(self):
        '''Save each cropped image.'''
        if hasattr(self.canvas, 'pil_img'):
            croppedimages, newfilenames = self.applyall()
            for image, filename in zip(croppedimages, newfilenames):
                image.save(filename)
            self.master.statusbar.update('Saved all images with prefix'
                                         'Multicropped-.')
        else:
            self.master.statusbar.update('Click Open.')


class MulticropApplication(tk.Frame):
    '''Main application for Multicrop.'''
    def __init__(self, root):
        tk.Frame.__init__(self, root)
        self.root = root

        yscrollbar = tk.Scrollbar(root)
        yscrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        xscrollbar = tk.Scrollbar(root, orient=tk.HORIZONTAL)
        xscrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas = tk.Canvas(self, 
                                width=400, height=300, 
                                yscrollcommand=yscrollbar.set, 
                                xscrollcommand=xscrollbar.set)

        self.statusbar = StatusBar(self)
        self.bottomframe = ButtonBar(self)
        self.b1 = 'up'
        self.xold = None
        self.yold = None

        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
        yscrollbar.config(command=self.canvas.yview)
        xscrollbar.config(command=self.canvas.xview)

        self.canvas.bind('<Motion>', self.motion)
        self.canvas.bind('<ButtonPress-1>', self.b1down)
        self.canvas.bind('<ButtonRelease-1>', self.b1up)

    def b1down(self, event):
        '''Left mouse down event. Initiate rectangle drawing.'''
        x = int(self.canvas.canvasx(event.x))
        y = int(self.canvas.canvasy(event.y))
        self.xold = x
        self.yold = y

        self.b1 = 'down'

    def b1up(self, event):
        '''Left mouse up event. End rectangle drawing.'''
        self.b1 = 'up'
        self.xold = None
        self.yold = None

    def motion(self, event):
        '''Mouse movement event. Create rectangle while mouse held down.'''
        global crop_coords
        if self.b1 == 'down':
            if self.xold is not None and self.yold is not None:
                self.canvas.delete('rect')
                xnew = int(self.canvas.canvasx(event.x))
                ynew = int(self.canvas.canvasy(event.y))
                crop_coords = (self.xold, self.yold, xnew, ynew)
                self.canvas.create_rectangle(*crop_coords, tags='rect', 
                                        width=2, outline='white')
                self.canvas.create_rectangle(*crop_coords, tags='rect', 
                                        width=2, dash=(4, 4))


def allimages(imgfiles):
    '''Determine if all given, selected files are images.'''
    for imgfile in imgfiles:
        if os.path.splitext(imgfile)[1] not in ('.png', 'jpg', 'jpeg'):
            return False
    return True


if __name__ == '__main__':
    root = tk.Tk()
    root.config(bg='black')
    MulticropApplication(root).pack(side='top', fill='both', expand=True)
    root.mainloop()