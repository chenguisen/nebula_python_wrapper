import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import numpy as np
def sem_analysis(sem_simu_result,image_path, plot = False, save = False):
	# Find out which file to open
	# if len(sys.argv) < 2:
	# 	print("No output file provided")
	# 	sys.exit()
	# sem_simu_result = sys.argv[1]
	if not os.path.exists(sem_simu_result):
		print("File {} cannot be found".format(sem_simu_result))
		sys.exit()


	# This is a numpy datatype that corresponds to output files
	electron_dtype = np.dtype([
		('x',  '=f'), ('y',  '=f'), ('z',  '=f'), # Position
		('dx', '=f'), ('dy', '=f'), ('dz', '=f'), # Direction
		('E',  '=f'),                             # Energy
		('px', '=i'), ('py', '=i')])              # Pixel index

	# Open the output file
	data = np.fromfile(sem_simu_result, dtype=electron_dtype)
	print("Number of electrons detected: {}".format(len(data)))


	# Make a histogram of pixel indices
	xmin = data['px'].min()
	xmax = data['px'].max()
	ymin = data['py'].min()
	ymax = data['py'].max()
	H, xedges, yedges = np.histogram2d(data['px'], data['py'],
		bins = [
			np.linspace(xmin-.5, xmax+.5, xmax-xmin+2),
			np.linspace(ymin-.5, ymax+.5, ymax-ymin+2)
		])

	if save:
		plt.imsave(image_path, H.T, cmap='gray')
	if plot:
		# Make a plot
		plt.imshow(H.T, cmap='gray')
		plt.xlabel('x pixel')
		plt.ylabel('y pixel')
		plt.show()

if __name__ == '__main__':
	sem_simu_result='/home/chenguisen/AISI/nebula/data/output.det'
	image_path='/home/chenguisen/AISI/nebula/data/output.png'
	sem_analysis(sem_simu_result, image_path, plot=True, save=True)