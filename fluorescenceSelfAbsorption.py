import h5py
import numpy as np
from matplotlib import pyplot as plt
from scipy import math
import cv2
import json
from TomopyReconstructionForFluorescenceTest import absorptionTomo,\
                                                    tomography, getData
import materialsData as mD

# Solve python2/3 (raw_)input compatibility issue
try:
    input = raw_input
except NameError:
    pass


class jsonDataFile():
    def __init__(self, file):
        self.file = file
        with open(self.file) as json_data_file:
            self.data = json.load(json_data_file)

    def getJsonData(self):
        return self.data

# NOTE Code only handles a single peak per material
# TODO Write some unit tests!!


class scan():
    def __init__(self, scanData):
        self._data = scanData.getJsonData()
        self._dataFolder = self._data["dataFolder"]

        self._absorptionProjections = self._data["absorptionTomo"]["path"]
        self._absorptionTomo()

        self._listOfMaterials = self._listMaterials()
        self._listOfMaterials = self._loadMassAttenuationCoefficients(
                                        self._listOfMaterials)
        self._outDir = self._data["outputFolder"]["path"]

        self._scanParameters = {}
        self._scanParameters["width"] = self._data["scanParameters"]["width"]
        self._scanParameters["height"] = self._data["scanParameters"]["height"]
        self._scanParameters["depthProjections"] = \
            self._data["scanParameters"]["depthProjections"]
        self._scanParameters["tomoCentre"] = \
            self._data["scanParameters"]["tomoCentre"]
        self._scanParameters["minFluoSignal"] = \
            self._data["scanParameters"]["minFluoSignal"]
        self._scanParameters["projShift"] = \
            self._data["scanParameters"]["projShift"]
        self._scanParameters["pixelSize"] = \
            self._data["scanParameters"]["pixelSize"]
        self._scanParameters["beamEnergy"] = \
            self._data["scanParameters"]["beamEnergy"]

    def printData(self):
        print(self._data)

    def getAbsorptionTomo(self):
        return self._absorptionTomo

    def getMaterials(self):
        return self._listOfMaterials

    def getAbsorptionProjections(self):
        return self._absorptionProjections

    def getScanParams(self):
        return self._scanParameters

    def getOutputDir(self):
        return self._outDir

    def getDataFolder(self):
        return self._dataFolder

    def _absorptionTomo(self):
        self._absorptionTomo = absorptionTomo(self).getAbsorptionTomo()

    def _listMaterials(self):
        matList = []
        for i in range(len(self._data["materials"]["name"])):
            newMat = mD.material(self._data["materials"]["name"][i])
            newMat.setPathToProjections(self._data["materials"]["path"][i])
            newMat.setPeak(self._data["materials"]["peak"][i])
            matList.append(newMat)
        return matList

    # TODO replace with method to use materialsData.py
    def _loadMassAttenuationCoefficients(self, listOfMaterials):
        print('loading mass attenuation coefficients...')

        massAttenuationCoefficients = \
            jsonDataFile("FluorescenceTestParameterFile.json")

        data2 = massAttenuationCoefficients.getJsonData()
        for i in range(len(listOfMaterials)):
            print('Setting up mass absorption coefficient for ',
                  listOfMaterials[i].getName())
            listOfMaterials[i].myDictionary = {}

            for j in range(len(listOfMaterials)):
                listOfMaterials[i].myDictionary[listOfMaterials[j].getName()] =\
                    data2[listOfMaterials[i].getName()][
                        listOfMaterials[j].getName()]
                listOfMaterials[i].myDictionary["Beam"] =\
                    data2[listOfMaterials[i].getName()]["Beam"]
            print('my dictionary', listOfMaterials[i].myDictionary)
        return listOfMaterials


class attenuationTable():
    def __init__(self, matList, scanParams):
        # create attenuationTable
        self._beamEnergy = scanParams["beamEnergy"]


class materialProjectionsTomo():
    def __init__(self, name, pathToProjection):
        self.name = name
        print('class defining material')
        # self.projections=pathToProjection
        self.path = pathToProjection

    def set_projection(self, projection):
        self.projection = projection

    def set_materialTomo(self, tomo):
        # self.tomo = np.zeros([angles,width,width])
        self.tomo = tomo


def loadMaterialTomos(nMaterials, listOfMaterials, dataFolder, tomoCentre):
    print('loading materials')
    print(nMaterials)
    materialsAnalysis = []
    print('loading data...')
    for i in range(nMaterials):
        print('Im happy here')
        temp = materialProjectionsTomo(
            listOfMaterials[i].getName(),
            listOfMaterials[i].getPathToProjections())
        print('path to projections', listOfMaterials[i].getPathToProjections())
        data = getData(temp.path, dataFolder)
        try:
            print(np.shape(np.array(data)))
            temp.set_projection(np.array(data))
            print('set_projection')
            materialsAnalysis.append(temp)
            print('appended')
            materialsAnalysis[i].set_materialTomo(
                tomography(materialsAnalysis[i].path, dataFolder,
                           tomoCentre, 1))
            print(materialsAnalysis[i].name,
                  'loaded and caluclated first tomography')
            plt.imshow(materialsAnalysis[i].tomo[0, :, :])
            plt.show()
            input("Press Enter to continue...")
        except KeyError:
            print("KeyError thrown: incorrect path to data")
            print(dataFolder, listOfMaterials[i].getPathToProjections(),
                  'not found! closing uffa')
    return materialsAnalysis


def AttenuationCorrection(scan, iterations):

    listOfMaterials = scan.getMaterials()
    nMaterials = len(listOfMaterials)

    scanParams = scan.getScanParams()
    tomoCentre = scanParams["tomoCentre"]
    minFluoSignal = scanParams["minFluoSignal"]
    projShift = scanParams["projShift"]
    pixelSize = scanParams["pixelSize"]

    '''
    trasmission through a pixel calculated from the transmission measured with
    the  Merlin: the effective density of Pt is found to be 1g/cm^3,
    for Cu 0.8g/cm^3
    '''
    # CuTransmThroughCu=0.999
    # CuTransmThroughPt=0.9951
    # PtTransmThroughCu=0.995
    # PtTransmThroughPt=0.996

    tomoMerlin = scan.getAbsorptionTomo()
    print("Showing first slice of absorption tomo")
    plt.imshow(tomoMerlin[0, :, :])
    plt.show()

    materialsAnalysis = loadMaterialTomos(nMaterials, listOfMaterials,
                                          scan.getDataFolder(), tomoCentre)

    testIteration = 0
    NewMaterials = [None] * nMaterials
    MaterialsCorrection = [None] * nMaterials
    # MaterialDensity = [None] * nMaterials
    # oscillation = np.zeros(iterations)

    vortexImPtCorr = [None] * nMaterials
    dsetImagePtCorr = [None] * nMaterials
    dsetOscillation = [None] * nMaterials

    for nMat in range(nMaterials):
            nameTomoMaterial = scan.getOutputDir() + \
                listOfMaterials[nMat].getName() + "Test21082018V3.hdf"

            height = 1
            print(nMat, np.shape(materialsAnalysis[nMat].projection))
            print('projection')
            plt.imshow(materialsAnalysis[nMat].projection[:, 0, :])
            plt.show()
            nAngles, height, width = np.shape(
                materialsAnalysis[nMat].projection)
            vortexImPtCorr[nMat] = h5py.File(nameTomoMaterial, "w")
            dsetImagePtCorr[nMat] = vortexImPtCorr[nMat].create_dataset(
                scan.getDataFolder(),
                (iterations+1, height, width, width), 'f')
            dsetOscillation[nMat] = vortexImPtCorr[nMat].create_dataset(
                'oscillation', (iterations+1,), 'f')

    while testIteration < iterations:
        if testIteration == 0:
            for nMat in range(nMaterials):
                dsetImagePtCorr[nMat][testIteration, :, :, :] = \
                    materialsAnalysis[nMat].tomo[:, :, :]
                print(np.shape(materialsAnalysis[nMat].tomo[:, :, :]))
                dsetOscillation[nMat][testIteration] = \
                    materialsAnalysis[nMat].tomo[0, 12, 12]
                print('saved',  materialsAnalysis[nMat].tomo[0, 12, 8])

        testIteration += 1
        print('iteration', testIteration)
        npdataMerlin = np.array(tomoMerlin)
        # a,b,c=np.shape(npdataMerlin)
        nAngles = 0
        height = 0
        width = 0
        # print(a,b,c, 'shape')
        # SumTotTomo=np.zeros(np.shape(tomoMerlin))
        for nMat in range(nMaterials):
            # print(nMat)

            # print('reconstruction done for ',
            #        materialsAnalysis[nMat].name)
            print(np.shape(materialsAnalysis[nMat].tomo))
            # SumTotTomo+=materialsAnalysis[nMat].tomo
            # print('VALUE',materialsAnalysis[nMat].tomo[0,10,10])
            plt.figure(1)
            plt.imshow(materialsAnalysis[nMat].tomo[0, :, :], 'Greys')
            # plt.show()
            # height=1
            nAngles, height, width = np.shape(
                materialsAnalysis[nMat].projection)
            NewMaterials[nMat] = np.zeros([nAngles, height, width])

            NewMaterials[nMat][:, :, 0] = materialsAnalysis[nMat]\
                .projection[:, :, 0]
            # print(nAngles,height,width, 'shape')
            MaterialsCorrection[nMat] = np.ones((nAngles, height,
                                                 width, width))
        print('tomography done, now Calculated Densities')
        print('VALUE', materialsAnalysis[1].tomo[0, 12, 12])
        # oscillation[testIteration-1]=materialsAnalysis[1].tomo[1,25,68]
        # input("Press Enter to continue...")
        materialRatio = [None]*nMaterials
        materialEffectiveDensity = [None]*height

        for heightIndex in range(height):
            effDens = np.zeros([width, width, nMaterials])
            for firstIndex in range(width):
                for secondIndex in range(width):
                    nonZerMat = 0
                    # sum = 0
                    nMat = 0
                    densitynonZeroMat = 1
                    pippo = 0
                    countMat = 0

                    '''
                    find a material if any exist at this scanning position
                    '''
                    for nonZerMat in range(nMaterials):
                        if materialsAnalysis[nonZerMat].tomo[
                            heightIndex, firstIndex,
                                secondIndex] > minFluoSignal:
                            if (firstIndex == 12 and secondIndex == 12):
                                print(firstIndex, secondIndex,
                                      nonZerMat, 'nonzeromat')
                            break

                    for nMat in range(nMaterials):
                        # effDensTemp=np.zeros([height,width,width])

                        # materialRatio[nMat]=materialsAnalysis[nMat].tomo[heightIndex,firstIndex,secondIndex]/SumTotTomo[heightIndex,firstIndex,secondIndex]
                        '''
                        calculate the material ratio
                        '''
                        if nMat == nonZerMat:
                            materialRatio[nMat] = 1
                        if materialsAnalysis[nonZerMat].tomo[
                            heightIndex, firstIndex,
                                secondIndex] > minFluoSignal:
                            bg1 = np.average(np.average(
                                materialsAnalysis[nMat].tomo[
                                    heightIndex, 0:5, 0:5]))
                            bg2 = np.average(np.average(
                                materialsAnalysis[nonZerMat].tomo[
                                    heightIndex, 0:5, 0:5]))
                            if (materialsAnalysis[nMat].tomo[
                                heightIndex, firstIndex,
                                    secondIndex]-bg1) > 0:
                                val1 = materialsAnalysis[nMat].tomo[
                                        heightIndex, firstIndex,
                                        secondIndex]-bg1
                            else:
                                val1 = 0
                            if materialsAnalysis[nonZerMat].tomo[
                                heightIndex, firstIndex,
                                    secondIndex]-bg2 > 0:
                                val2 = materialsAnalysis[nonZerMat].tomo[
                                    heightIndex, firstIndex,
                                    secondIndex]-bg2
                            else:
                                val2 = 0
                            if val2 > 0:
                                materialRatio[nMat] = val1/val2
                            else:
                                materialRatio[nMat] = 1
                        else:
                            materialRatio[nMat] = 0

                        if materialRatio[nMat] > 0:
                            pippo += materialRatio[nMat]\
                                * listOfMaterials[nMat].myDictionary['Beam']
                            countMat += 1

                    '''
                    calculate density of the non zero material
                    '''
                    if pippo > 0:

                        # print('absorption value ', npdataMerlin[
                        #    heightIndex, firstIndex, secondIndex])
                        densitynonZeroMat = npdataMerlin[
                            heightIndex, firstIndex, secondIndex]\
                            / (pippo * pixelSize)
                        if (firstIndex == 12 and secondIndex == 12):
                            print('density non zero mat',
                                  densitynonZeroMat, pippo,
                                  listOfMaterials[nonZerMat
                                                  ].myDictionary['Beam'],
                                  nonZerMat, materialRatio[1])
                            print('absorption value  ',
                                  npdataMerlin[heightIndex,
                                               firstIndex, secondIndex])
                    else:
                        densitynonZeroMat = 0
                    '''
                    calculate the density for all the other materials
                    '''

                    for nMat in range(nMaterials):
                        effDens[firstIndex, secondIndex, nMat] = \
                            densitynonZeroMat * materialRatio[nMat]
                        if (firstIndex == 12 and secondIndex == 12):
                            print(effDens[firstIndex, secondIndex, nMat], nMat)

            materialEffectiveDensity[heightIndex] = effDens
        plt.figure(100)
        plt.imshow(materialEffectiveDensity[0][:, :, 0])
        plt.colorbar()
        plt.clim(0, 0.5)
        plt.figure(200)
        plt.imshow(materialEffectiveDensity[0][:, :, 1])
        plt.colorbar()
        plt.clim(0, 0.5)
        plt.show()

        MaterialCorrection = np.ones((nMaterials, nAngles,
                                      height, width, width))

        print('doing correction')
        shift = projShift
        minimum = 0.002
        maximum = 0.05

        # generalDensity = 0
        '''
        this shift is due to the centre of rotation,
        the centre of rotation is 23,
        the centre of the reconstruction is 43,
        so I need to shift 20 pixels to have the profile coincide
        '''
        # xplot = np.linspace(0, width-1, width)
        for i in range(0, nAngles):
            # print('angle', i)
            for k in range(height):
                # print('slice',k)
                '''
                rotating absorption
                '''
                M = cv2.getRotationMatrix2D((width/2, width/2), -i, 1)
                merlinSlice = npdataMerlin[k, :, :]
                dst = cv2.warpAffine(merlinSlice, M, (width, width))
                dstShifted = np.zeros((width, width))
                dstShifted[0:width-1-shift, :] = dst[shift:width-1, :]
                binaryMask = np.zeros((width, width))

                # MaterialSlice = [None]*nMaterials
                dstShiftedMaterial = [None]*nMaterials
                shiftedMaterialDensity = [None]*nMaterials
                binaryMaskMaterial = [None]*nMaterials
                '''
                rotating fluorescence and density
                '''

                for nMat in range(nMaterials):

                    '''
                    rotate tomography of each material
                    '''
                    dstMaterial = cv2.warpAffine(
                        materialsAnalysis[nMat].tomo[k, :, :],
                        M, (width, width))
                    dstShiftedMaterial[nMat] = np.zeros((width, width))
                    binaryMaskMaterial[nMat] = np.zeros((width, width))
                    '''
                    shift the rotated material
                    '''
                    dstShiftedMaterial[nMat][0:width-1-shift, :] = \
                        dstMaterial[shift:width-1, :]
                    shiftedMaterialDensity[nMat] = np.zeros([width, width])
                    '''
                    shift material density
                    '''
                    shiftedMaterialDensity[nMat][0:width-1-shift, :] = \
                        cv2.warpAffine(
                            materialEffectiveDensity[k][:, :, nMat],
                            M, (width, width))[shift:width-1, :]
                    # print(' density', nMat,
                    # materialEffectiveDensity[k][12,8,nMat])
                    # plt.imshow(materialEffectiveDensity[k][:,:,nMat])
                    # plt.show()
                    # shiftedMaterialDensity[nMat]=cv2.warpAffine(materialEffectiveDensity[k][:,:,nMat],M,(width,width))

                # print('creating masks...')
                for kk in range(width):
                    for ll in range(width):
                        if (dstShifted[kk, ll] > minimum)\
                                and (dstShifted[kk, ll] < maximum):
                                    binaryMask[kk, ll] = 1
                        for nMat in range(nMaterials):
                            minFluoSignal = np.average(np.average(
                                materialsAnalysis[nMat].tomo[0, 0:5, 0:5]))
                            if (dstShiftedMaterial[nMat][kk, ll]
                                    > minFluoSignal):
                                binaryMaskMaterial[nMat][kk, ll] = 1

                '''
                print(nMat, 'material')
                plt.imshow(binaryMaskMaterial[0][:,:])
                plt.show()
                plt.imshow(binaryMaskMaterial[1][:,:])
                plt.show()
                '''
                for j in range(0, width):
                    for ll in range(0, j-1):
                        '''
                        correct the new mask for my mask
                        For Cu first and Pt then
                        '''

                        averageDensityMaterial = np.zeros(len(
                            listOfMaterials))

                        for nMat in range(nMaterials):

                            '''
                            profllMaterial thickness in
                            pixel of the material at ll
                            '''
                            profllMaterial = binaryMask[ll, :] \
                                * binaryMaskMaterial[nMat][j, :]
                            correction = 1
                            nMat2 = 0
                            for nMat2 in range(nMaterials):

                                profllDensMaterial = \
                                    shiftedMaterialDensity[nMat2][ll, :]\
                                    * binaryMaskMaterial[nMat][j, :]
                                profThickMaterial = np.sum(profllMaterial)
                                profDensMaterial = np.sum(
                                    profllDensMaterial)
                                if profThickMaterial > 0:
                                    averageDensityMaterial[nMat2] = \
                                        profDensMaterial/profThickMaterial
                                else:
                                    averageDensityMaterial[nMat2] = 0
                                correction = correction * math.exp(
                                    -averageDensityMaterial[nMat2]
                                    * listOfMaterials[nMat2].myDictionary[
                                        listOfMaterials[nMat].getName()]
                                    * pixelSize)

                            MaterialCorrection[nMat, i, k, j, ll] = correction

                    NewCorrectionMaterial = np.ones(nMaterials)

                    for lll in range(j):
                        for nMat in range(nMaterials):
                            NewCorrectionMaterial[nMat] *=\
                                MaterialCorrection[nMat, i, k, j, lll]
                    '''
                    here correct the projection for the attenuation
                    '''
                    for nMat in range(nMaterials):

                        NewMaterials[nMat][i, k, j] =\
                            materialsAnalysis[nMat].projection[i, k, j]\
                            / NewCorrectionMaterial[nMat]
                        'correcting here for re-emission'
                        if nMat == 1:
                            NewMaterials[0][i, k, j] =\
                                NewMaterials[0][i, k, j]\
                                - (NewMaterials[nMat][i, k, j]
                                    - materialsAnalysis[nMat].
                                    projection[i, k, j])

        print('all done, writing file for each material....')

        tomoNew = [None]*nMaterials
        for nMat in range(nMaterials):
            nameMat = scan.getOutputDir() + "testProjections" + \
                listOfMaterials[nMat].getName() + "21082018V3.hdf"
            vortexImPt = h5py.File(nameMat, "w")
            dsetImagePt = vortexImPt.create_dataset(
                scan.getDataFolder(), (nAngles, height, width), 'f')
            dsetImagePt[...] = NewMaterials[nMat]  # /myMax
            vortexImPt.close()
            listOfMaterials[nMat].path = nameMat
            # listOfMaterials[nMat].setPathToProjections(nameMat)
            print('processing the new tomography')
            tomoNew[nMat] = tomography(nameMat, scan.getDataFolder(),
                                       tomoCentre, 1)
            plt.figure(1)
            plt.imshow(materialsAnalysis[nMat].tomo[0, :, :])

            plt.figure(2)
            plt.imshow(tomoNew[nMat][0, :, :])
            materialsAnalysis[nMat].set_materialTomo(tomoNew[nMat])
            dsetImagePtCorr[nMat][testIteration, :, :, :] = tomoNew[nMat]
            dsetOscillation[nMat][testIteration] =\
                materialsAnalysis[nMat].tomo[0, 12, 8]
    for nMat in range(nMaterials):
        vortexImPtCorr[nMat].close()

    print('all done, all closed')


# For testing function
if __name__ == "__main__":

    scanData = jsonDataFile("ScanData.json")
    nIterations = 5
    scan = scan(scanData)

    AttenuationCorrection(scan, nIterations)
