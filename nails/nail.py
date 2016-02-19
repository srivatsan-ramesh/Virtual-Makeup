from scipy import interpolate
from pylab import *
from skimage import color

Rg, Gg, Bg = (207.,40.,57.)

texture_input = 'texture1.jpg'

def getBoundaryPoints(x, y):
	tck,u = interpolate.splprep([x, y], s=0, per=1)
	unew = np.linspace(u.min(), u.max(), 1000)
	xnew,ynew = interpolate.splev(unew, tck, der=0)
	tup = c_[xnew.astype(int),ynew.astype(int)].tolist()
	coord = list(set(tuple(map(tuple, tup))))
	coord = np.array([list(elem) for elem in coord])
	return coord[:,0],coord[:,1]
	
def getInteriorPoints(x, y):
	nailx = []
	naily = []
	def ext(a, b, i):
		a, b=round(a), round(b)
		nailx.extend(arange(a, b, 1).tolist())
		naily.extend((ones(b-a)*i).tolist())
	x, y = np.array(x), np.array(y)
	xmin, xmax = amin(x), amax(x)
	xrang = np.arange(xmin, xmax + 1, 1)
	for i in xrang:
		ylist = y[where(x==i)]
		ext(amin(ylist), amax(ylist), i)
	return nailx, naily

im = imread('nail_inp.jpg')
text = imread(texture_input)
def applyNailPolish(x , y , r = Rg, g = Gg, b = Bg):
	val = color.rgb2lab((im[x, y]/255.).reshape(len(x), 1, 3)).reshape(len(x), 3)
	L, A, B = mean(val[:,0]), mean(val[:,1]), mean(val[:,2])
	L1, A1, B1 = color.rgb2lab(np.array((r/255., g/255., b/255.)).reshape(1, 1, 3)).reshape(3,)
	ll, aa, bb = L1 - L, A1 - A, B1 - B
	val[:, 0] = np.clip(val[:, 0] + ll, 0, 100)
	val[:, 1] = np.clip(val[:, 1] + aa, -127, 128)
	val[:, 2] = np.clip(val[:, 2] + bb, -127, 128)
	im[x, y] = color.lab2rgb(val.reshape(len(x), 1, 3)).reshape(len(x), 3)*255

def applyTexture(x, y):
	xmin, ymin = amin(x),amin(y)
	X = (x-xmin).astype(int)
	Y = (y-ymin).astype(int)
	val1 = color.rgb2lab((text[X, Y]/255.).reshape(len(X), 1, 3)).reshape(len(X), 3)
	val2 = color.rgb2lab((im[x, y]/255.).reshape(len(x), 1, 3)).reshape(len(x), 3)
	L, A, B = mean(val2[:,0]), mean(val2[:,1]), mean(val2[:,2])
	val2[:, 0] = np.clip(val2[:, 0] - L + val1[:,0], 0, 100)
	val2[:, 1] = np.clip(val2[:, 1] - A + val1[:,1], -127, 128)
	val2[:, 2] = np.clip(val2[:, 2] - B + val1[:,2], -127, 128)
	im[x, y] = color.lab2rgb(val2.reshape(len(x), 1, 3)).reshape(len(x), 3)*255

points = np.loadtxt('nailpoint')

x, y = points[:12, 0],points[:12, 1]
x, y = getBoundaryPoints(x, y)
x, y = getInteriorPoints(x, y)
#applyNailPolish(x, y)
applyTexture(x, y)

x, y = points[12:24, 0],points[12:24, 1]
x, y = getBoundaryPoints(x, y)
x, y = getInteriorPoints(x, y)
#applyNailPolish(x, y)
applyTexture(x, y)

x, y = points[24:36, 0],points[24:36, 1]
x, y = getBoundaryPoints(x, y)
x, y = getInteriorPoints(x, y)
#applyNailPolish(x, y)
applyTexture(x, y)

x, y = points[36:, 0],points[36:, 1]
x, y = getBoundaryPoints(x, y)
x, y = getInteriorPoints(x, y)
#applyNailPolish(x, y)
applyTexture(x, y)

figure()
imshow(im)
imsave('output_texture.jpg',im)
show()
