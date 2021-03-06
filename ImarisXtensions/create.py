#
#
#  SurfacesSplit XTension  
#
#  Copyright Bitplane AG
#
#    <CustomTools>
#      <Menu>
#       <Item name="create" icon="Python3" tooltip="Reconstruct 3D surface from sliced spinal cord sections.">
#         <Command>Python3XT::create(%i)</Command>
#       </Item>
#      </Menu>
#    </CustomTools>

'''
Author Notes:
- This is the first script to run in 3D Reconstruction
- Make sure to have your IMARIS version correct on lines 30-31
- 
'''

import sys 
import time
import colorama
colorama.init(autoreset=True)
import numpy as np	

sys.path.append("C:\Program Files\Bitplane\Imaris x64 9.7.2\XT\python3") # unique path to you 
sys.path.append("C:\Program Files\Bitplane\Imaris x64 9.7.2\Imaris.exe") # unique path to you 

import ImarisLib
	
def test(aImarisId):

	# Create an ImarisLib object
	vImarisLib = ImarisLib.ImarisLib()

	# Get an imaris object with id aImarisId
	vImaris = vImarisLib.GetApplication(aImarisId)

	# Check if the object is valid
	if vImaris is None:
		
		print('Could not connect to Imaris!')
		# Sleep 2 seconds to give the user a chance to see the printed message
		time.sleep(2)
		return
	
	# Get the factory
	vFactory = vImaris.GetFactory()

	# Get the surpass scene
	vSurpassScene = vImaris.GetSurpassScene()
	
	# This XTension requires a loaded dataset
	if vSurpassScene is None:
		print('Please create some Surfaces in the Surpass scene!')
		time.sleep(2)
		return
	
	try: 
		# Get the Surfaces (Each Surface has a unique Surface Index and a Surface ID)
		vSurfaces = vFactory.ToSurfaces(vImaris.GetSurpassSelection())

		if vSurfaces is None:
			print('Please select some surfaces in the surpass scene!')
			time.sleep(2)
			return

		# GET IDS SURFACES GET IDS () 
		ids = vSurfaces.GetIds()
		sdl = [] #Surface Data Layout Array

		for i in range(len(ids)):
			if(vSurfaces.GetSurfaceDataLayout(i).mSizeX < (0.1 * vImaris.GetImage(0).GetSizeX())): #we ignore the smaller artifacts
				continue
			sdl.append(vSurfaces.GetSurfaceDataLayout(i))

		sdl.sort(reverse = True, key = lambda x : x.mExtendMaxY) #check markdown for more detail on why we sort it like this
		
		print("\033[92m Printing Surface Data Layout Array \033[92m")
		print(sdl)
		print("\033[92m Finished Printing Surface Data Layout Array \033[92m")

		'''
		This commented out section is a wellness check that I recommend you perform to make sure the dataset is clean
		
	
		#next task is to get max x and y array
		xsizearray, ysizearray, extendxsizeMaxarray = ([] for i in range(3))
		for i in sdl:
			xsizearray.append(i.mSizeX)
			ysizearray.append(i.mSizeY)
			extendxsizeMaxarray.append(i.mExtendMaxX)

		print('here is the xsize array:' , xsizearray)
		print('')
		print('\nhere is the ysize array:' , ysizearray)
		print('')
		print('\nhere is the extendXsizeMaxarray:' , extendxsizeMaxarray)
		print('')
		print('\n The Length of mExtendMaxX array is:L', len(extendxsizeMaxarray)) 
		print('')
		time.sleep(1)
		'''

		imagedataset = vImaris.GetImage(0)
		print("\033[92m Printing imagedataset now \033[92m")
		print(imagedataset)
		print(imagedataset.GetExtendMinX())
		time.sleep(1)
		xdatamin = imagedataset.GetExtendMinX()
		xdatamax = imagedataset.GetExtendMaxX()
		ydatamin = imagedataset.GetExtendMinY()
		ydatamax = imagedataset.GetExtendMaxY()
		zdatamin = imagedataset.GetExtendMinZ()
		zdatamax = imagedataset.GetExtendMaxZ()

		vx = (xdatamax - xdatamin) / (imagedataset.GetSizeX()) 
		vy = (ydatamax - ydatamin) / (imagedataset.GetSizeY())
		vz = (zdatamax - zdatamin) / (imagedataset.GetSizeZ())

		maxX = max(xsizearray)
		maxY = max(ysizearray)
		z = len(sdl)
		data = np.zeros((maxX, maxY, z , imagedataset.GetSizeC(), 1), dtype = np.float32) #make an empty data container of the same dimensions

		print('maxX: ',maxX)
		print('maxY: ', maxY)
		print('z: ', z)
		print('',imagedataset.GetSizeC())
		time.sleep(1)


		print(vx)
		print(vy)
		print(vz)
		time.sleep(2)

		x = int(sdl[0].mExtendMaxX)
		y = int(sdl[0].mExtendMaxY)
		z = int(sdl[0].mExtendMaxZ)

		print(x,y,z)

		print('fin')

		
		for i,id in enumerate(sdl): #use the sorted array and check if the indexes match the slice numbers
			
			vx1min = (id.mExtendMinX - xdatamin)/vx # left corner of a rectangular slice, since original axis starts at n, we want  to translate that into a new data array that starts at 0
			vy1min = (id.mExtendMinY - ydatamin)/vy # bottom corner of a rectangular slice
			vz1min = (id.mExtendMinZ - (zdatamin))/vz
			print('Working on Surface:', i)
			print('id.mextendminz is ', id.mExtendMinZ)
			print('zdatamin is ', zdatamin)
			print('For Surface: ', i, " the vz1min value is: ",vz1min)
			print(id.mSizeZ)
			print('\n')

			print(np.shape(imagedataset.GetDataSubVolumeFloats(vx1min, vy1min, vz1min, 0, 0, id.mSizeX, id.mSizeY, 1)))
	
			for channel in range(0, 3):
				print('Working on Channel:', channel)
				data[0:id.mSizeX, 0:id.mSizeY, i, channel] = imagedataset.GetDataSubVolumeFloats(vx1min, vy1min, vz1min, channel, 0, id.mSizeX, id.mSizeY, 1) #gives data for 1 channel
		
		np.save("D:\Geet\mos22slide9.npy", data) 

		
		#Now  you have saved a single column ims file as a numpy array. Once you have the second numpy file, run the second script that combines both these files.
		
		

	except Exception:
		import traceback
		traceback.print_exc()
		input()