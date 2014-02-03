from tkinter import *
from tkinter import filedialog
from PIL import ImageTk, Image
import os


b1 = 'up'
xold = None
yold = None
crop_coords = None
crops = []
imgfiles = None

root = Tk(className="Image viewer")
root.config(bg="black")
canvas_width = 800
canvas_height = 600


def openimage():
    '''Select all images to crop. Display first to screen.'''
    global imgfiles, crops
    try:
        imgfiles = filedialog.askopenfilenames()
        imgfile = imgfiles[0]
        print(imgfile)
        if imgfile:
            canvas.pil_img = Image.open(imgfile)
            canvas.config(width=canvas.pil_img.size[0])
            canvas.config(height=canvas.pil_img.size[1])
            set_canvas_image(canvas.pil_img)
            crops = []
    except IOError:
        openimage()


def set_canvas_image(img):
    '''Set canvas to display only the given image.'''
    canvas.img = ImageTk.PhotoImage(img)
    canvas.create_image(0,0, anchor=NW, image=canvas.img) 
    
    canvas.configure(
            scrollregion=(0,0,canvas.img.width(), canvas.img.height()))


def b1down(event):
    '''Left mouse down event. Initiate rectangle drawing.'''
    global b1, xold, yold
    canvas = event.widget
    x = int(canvas.canvasx(event.x))
    y = int(canvas.canvasy(event.y))
    xold = x
    yold = y

    b1 = 'down'


def b1up(event):
    '''Left mouse up event. End rectangle drawing.'''
    global b1, xold, yold
    b1 = 'up'
    xold = None
    yold = None


def motion(event):
    '''Mouse movement event. Create rectangle while left mouse held down.'''
    global crop_coords
    if b1 == 'down':
        global xold, yold
        if xold is not None and yold is not None:
            canvas.delete('rect')
            xnew = int(canvas.canvasx(event.x))
            ynew = int(canvas.canvasy(event.y))
            crop_coords = (xold, yold, xnew, ynew)
            canvas.create_rectangle(*crop_coords, tags='rect', outline='white')
            canvas.create_rectangle(*crop_coords, tags='rect', dash=(4, 4))


def crop():
    '''Crop image on canvas according to created rectangle'''
    global crop_coords
    
    if crop_coords is None or not hasattr(canvas, 'pil_img'):
        return

    # order the rectangle's coordinates to be (left, top, right, bottom)
    ordered_coords = (
            min(crop_coords[0], crop_coords[2]),
            min(crop_coords[1], crop_coords[3]),
            max(crop_coords[0], crop_coords[2]),
            max(crop_coords[1], crop_coords[3]),
            )

    print('Cropping rectangle at ' + str(ordered_coords))
    canvas.delete('rect')
    canvas.pil_img = canvas.pil_img.crop(ordered_coords)
    set_canvas_image(canvas.pil_img)

    canvas.config(width=ordered_coords[2]-ordered_coords[0])
    canvas.config(height=ordered_coords[3]-ordered_coords[1])
    crops.append(ordered_coords)
    crop_coords = None


def applyall():
    '''Apply all crops to all selected image files.'''
    global imgfiles
    global crops
    croppedimages = [canvas.pil_img]
    newfilenames = ['/Multicropped-'.join(os.path.split(imgfiles[0]))]
    for imgfile in imgfiles[1:]:  # imgfiles[0] already cropped.
        image = Image.open(imgfile)
        for cropping in crops:
            image = image.crop(cropping)
        croppedimages.append(image)
        newfilenames.append('/Multicropped-'.join(os.path.split(imgfile)))

    return croppedimages, newfilenames


def saveimages():
    '''Save each cropped image.'''
    if hasattr(canvas, 'pil_img'):
        croppedimages, newfilenames = applyall()
        for image, filename in zip(croppedimages, newfilenames):
            image.save(filename)   



yscrollbar = Scrollbar(root)
yscrollbar.pack(side=RIGHT, fill=Y)

xscrollbar = Scrollbar(root, orient=HORIZONTAL)
xscrollbar.pack(side=BOTTOM, fill=X)

canvas = Canvas(root, width=canvas_width, height=canvas_height, yscrollcommand=yscrollbar.set, xscrollcommand=xscrollbar.set)
button = Button(root, text="Open", command=openimage)
button.pack(side=BOTTOM)
button_save = Button(root, text='Save', command=saveimages)
button_save.pack(side=BOTTOM)
button_crop = Button(root, text='Crop', command=crop)
button_crop.pack(side=BOTTOM)


canvas.pack(side=TOP, fill=BOTH, expand=YES)
yscrollbar.config(command=canvas.yview)
xscrollbar.config(command=canvas.xview)

canvas.bind("<Motion>", motion)
canvas.bind("<ButtonPress-1>", b1down)
canvas.bind("<ButtonRelease-1>", b1up)

mainloop()