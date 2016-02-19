from scipy import interpolate
from pylab import *
from skimage import color
import cv2

Rg, Gg, Bg = (223.,91.,111.)
intensity = 0.5 #intensity of the blush
mid = 378	#Approx x coordinate of center of the face.
'''
mid is used to construct the points for the blush in
the left cheek , as only the right cheek's points are
given as input.
'''
im = imread('Input1.jpg')
points = np.loadtxt('point1.txt')

height,width = im.shape[:2]
imOrg=im.copy()

def getBoundaryPoints(x , y):
 tck,u = interpolate.splprep([x, y], s=0, per=1)
 unew = np.linspace(u.min(), u.max(), 1000)
 xnew,ynew = interpolate.splev(unew, tck, der=0)
 tup = c_[xnew.astype(int),ynew.astype(int)].tolist()
 coord = list(set(tuple(map(tuple, tup))))
 coord = np.array([list(elem) for elem in coord])
 return coord[:,0],coord[:,1]

def getInteriorPoints(x , y):
 intx = []
 inty = []
 def ext(a, b, i):
  a, b=round(a), round(b)
  intx.extend(arange(a, b, 1).tolist())
  inty.extend((ones(b-a)*i).tolist())
 x, y = np.array(x), np.array(y)
 xmin, xmax = amin(x), amax(x)
 xrang = np.arange(xmin, xmax+1, 1)
 for i in xrang:
  ylist = y[where(x==i)]
  ext(amin(ylist), amax(ylist), i)
 return inty, intx

def applyBlushColor(r = Rg, g = Gg, b = Bg):
 global im
 val = color.rgb2lab((im/255.)).reshape(width*height, 3)
 L, A, B = mean(val[:,0]), mean(val[:,1]), mean(val[:,2])
 L1, A1, B1 = color.rgb2lab(np.array((r/255., g/255., b/255.)).reshape(1, 1, 3)).reshape(3,)
 ll, aa, bb = (L1 - L)*intensity, (A1 - A)*intensity, (B1 - B)*intensity
 val[:, 0] = np.clip(val[:, 0] + ll, 0, 100)
 val[:, 1] = np.clip(val[:, 1] + aa, -127, 128)
 val[:, 2] = np.clip(val[:, 2] + bb, -127, 128)
 im = color.lab2rgb(val.reshape(height, width, 3))*255

def smoothenBlush(x, y):
 global imOrg
 imgBase=zeros((height,width))
 cv2.fillConvexPoly(imgBase,np.array(c_[x, y],dtype = 'int32'),1)
 imgMask=cv2.GaussianBlur(imgBase,(51,51),0)
 imgBlur3D=np.ndarray([height,width,3],dtype='float')
 imgBlur3D[:,:,0]=imgMask
 imgBlur3D[:,:,1]=imgMask
 imgBlur3D[:,:,2]=imgMask
 imOrg=(imgBlur3D*im+(1-imgBlur3D)*imOrg).astype('uint8')

x, y = points[0:5, 0],points[0:5, 1]
x, y = getBoundaryPoints(x, y)
x, y = getInteriorPoints(x, y)
applyBlushColor()
smoothenBlush(x, y)
smoothenBlush(2*mid*ones(len(x))-x, y)

figure()
plt.imshow(imOrg)
imsave('output.jpg',imOrg)
show()
