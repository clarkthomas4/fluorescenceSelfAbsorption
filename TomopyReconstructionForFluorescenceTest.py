import h5py
import tomopy
import numpy as np
# from matplotlib import pyplot as plt
# from scipy import math


def tomography(nxsfileName, dataFolder, centre, index):
    print('file containing projections', nxsfileName)

    mypath = h5py.File(nxsfileName, 'r')
    theta = tomopy.angles(25, 0, 180)
    # print('angles', theta)

    print('looking for "', dataFolder, '" in the tree...')
    contLoop = True
    pathTot = ''
    mycent = centre  # 32 for Cu and Pt
    contLoop, pathToData, pathTot = myRec(mypath, contLoop,
                                          pathTot, dataFolder)
    print(pathTot)
    if not contLoop:
        if index == 0:
            print('database "', dataFolder, '" found in  ', pathTot)
            print('for merlin')
            data = mypath[str(pathTot)]
            npdata = np.array(data)
            print(npdata.shape)
            a, b = npdata.shape
            pippo = np.zeros((a, 1, b))
            pippo[:, 0, :] = data
            # height=breakwidth=c
            # print(a,b,c, ' file images to analyse')
            # print('I look for the center...')
            # cen= tomopy.find_center(npdata, theta, init=mycent,ind=0,tol=0.5)
            # print(cen)
            # plt.imshow(npdata[:,1,:])
            # plt.show()

            print('removing stripes...')
            # filtered=tomopy.remove_stripe_fw(npdata, level=20, wname='db5',
            #                                  sigma=1, pad=1)
            # norm=tomopy.normalize_roi(npdata, roi=[0,80,9,85])
            # filtered=tomopy.remove_stripe_fw(norm, level=0, wname='haar',
            #                                  sigma=0.1, pad=0)
            # print 'reconstructing...'

            pippo = tomopy.minus_log(pippo)
        else:
            print('database "', dataFolder, '" found in  ', pathTot)

            data = mypath[str(pathTot)]
            npdata = np.array(data)
            print(npdata.shape)
            a, b, c = npdata.shape
            # pippo=np.zeros((a,1,b))
            pippo = data
            print(pippo.dtype)
            print('here pt loaded')
            # plt.imshow(npdata[:,0,:])
            # plt.show()
        # rec = tomopy.recon(npdata, theta, 27, algorithm='gridrec')
        # rec=tomopy.circ_mask(rec, axis=0, ratio=0.95)
        # rec = tomopy.recon(filtered, theta, 32, algorithm='gridrec')
        rec = tomopy.recon(pippo, theta, mycent, algorithm='mlem', num_iter=40)
        # 'osem''ospml_hybrid', num_iter=100)#algorithm='gridrec')
        # recRingless=tomopy.remove_ring(rec,43,43,rwidth=1,theta_min=20,
        #    thresh=1,thresh_max=0.4, thresh_min=-0.4)

        # Fig1=plt.figure(1)
        # plt.imshow(rec[1,:,:],cmap='Greys_r')

        print('reconstruction done! this is the shape of the reconstructed '
              'object:', np.shape(rec))
        # Fig2=plt.figure(2)
        # plt.imshow(filtered[5][:][:])
        # plt.show()
        # plt.imshow(rec[0,:,:])
        # plt.show()
        # width=86
        # height=10
        # a,b,c=rec.shape
        '''
        name="/dls/i13-1/data/2017/cm16785-1/processing/VortexTomo/vortexTomoPtAttenuation0103.hdf"#vortexTomoCuNewAttenuation.hdf"
        #name2="/dls/i13-1/data/2017/cm16785-1/processing/VortexTomo/vortexTomoCuNew.tiff"
        #name="/dls/i13-1/data/2017/cm16785-1/processing/merlinTomo/merlinTomo.hdf"
        merlinTomo=h5py.File(name,"w")


        print('Im copying...')
        dsetImage=merlinTomo.create_dataset('data', (height,width,width), 'f')
        dsetImage[...]=rec
        merlinTomo.close()
        '''
        # tomopy.write_tiff_stack(rec, name2)
        print('done, file closed')
        mypath.close()
        return rec

    else:
        print('database "', dataFolder, '" not found!')
    mypath.close()


def myRec(obj, continueLoop, pathTot, dataFolder):
    '''
    recursive function to look for the data database
    '''
    temp = None
    i = 1
    tempPath = ''
    for name, value in obj.items():
        if continueLoop:
            # check if the object is a group
            if isinstance(obj[name], h5py.Group):
                tempPath = '/' + name
                if len(obj[name]) > 0:
                    continueLoop, temp, tempPath = \
                        myRec(obj[name], continueLoop, tempPath, dataFolder)
                else:
                    continue
            else:
                test = obj[name]
                temp1 = '/' + dataFolder
                if temp1 in test.name:
                    continueLoop = False
                    tempPath = pathTot+'/'+name
                    return continueLoop, test.name, tempPath
            i = i + 1
        if (i-1) > len(obj.items()):
            tempPath = ''
    pathTot = pathTot + tempPath
    return continueLoop, temp, pathTot


def getDataPath(h5File, dataFolder):
    '''
    Wrapper function to use myRec
    '''
    myPath = h5py.File(h5File, 'r')
    print('looking for "', dataFolder, '" in the tree...')
    contLoop = True
    pathTot = ''
    contLoop, pathToData, pathTot = myRec(myPath, contLoop,
                                          pathTot, dataFolder)

    if (contLoop):
        print('database "', dataFolder, '" not found!')
    else:
        print('database "', dataFolder, '" found in  ', pathTot)
        return contLoop, pathTot


# For testing function
if __name__ == "__main__":
    # pathToNexustomoData='/dls/i13-1/data/2017/cm16785-1/processing/merlinTomo/merlinProjections.hdf'
    pathToNexustomoData = ('/dls/i13-1/data/2017/cm16785-1/processing/Vortex'
                           'Tomo/vortexProjectionsPtAttenuation0103.hdf')
    centre = 23
    # width=

    # missing projections
    # mypath=h5py.File(nxsfileName,'r')
    # name='C:\\Users\\xfz42935\\Documents\\Alignement\\pco1-63429.hdf'
    '''
    findContour(<pathToNexusFile>,<nameOfTheEntry>,minimumEnergy,MaximumEnergy,xLenghtOfPtychoScan,yLenghtofPtychoScan)
    nameofTheEntry is 'fullSpectrum' for vortex, PCO or Merlin is 'data'
    '''
    img = tomography(pathToNexustomoData, 'data', centre)
    # plt.imshow(img[1,:,:])
    # plt.show()
    # findContour(pathToNexus,'fullSpectrum',9.3,9.6,86,10)
