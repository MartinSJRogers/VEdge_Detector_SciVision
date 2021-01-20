# Python modules to import
import gdal
import tensorflow as tf
from tensorflow.keras.models import model_from_json
import numpy as np
from PIL import Image
from rasterio.plot import show
import rasterio
import skimage.transform

########Parameters you can alter##############
#Image to run through VEdge_Detector tool
testImage= "bribie_island.tif"
#State whether to save the output image to your directory. Values: 'yes' or 'no'
Export_Image= 'no'
#Define output image name. Image is placed in same directory as input images.
#All names must finish with '.tif' e.g 'output.tif'
Output_Image_Name= 'bribie_output.tif'

##############################################################################
######################Do not change code under this line #####################
##############################################################################

###CNN model and weights#####
#model_fp="C:/Users/msjr2/Documents/Cambridge/hpc/ModelgdalGRNIR.json"  
#weights_fn = "C:/Users/msjr2/Documents/Cambridge/hpc/weights-advancementsgdalGRNIR11-64-0.00.hdf5"
model_fp="C:/Users/msjr2/Documents/Cambridge/machineLearning/firstPythons/Keras_HED/checkpoints/HEDSeg/Modelpython38.json"
weights_fn="C:/Users/msjr2/Documents/Cambridge/hpc/weightAdvancements/weights-advancementsMarch-02-0.26.hdf5"


import os
currentFile=os.path.abspath(__file__).replace("\\","/")
print(currentFile)
directory_name= currentFile.rsplit('/',1)[0]
print(directory_name)


testImage=str(directory_name) + '/' + str(testImage) 
print(str(testImage))
#Open image and rearrange raster bands
rawImage=gdal.Open(testImage)
bandCount=rawImage.RasterCount
if bandCount>1: 
    raster=rawImage.ReadAsArray()
    rasArrSwap= np.swapaxes(raster, 0,2)
    rasArrSwap= np.swapaxes(rasArrSwap, 0,1)
    
    #image band selection- Red, Green, NIR    
    if bandCount==5:
        rasArrFinal=np.concatenate((rasArrSwap[:, :, 1:3], rasArrSwap[:, :, 4:]), axis=2)
    elif bandCount==4:
        rasArrFinal=np.concatenate((rasArrSwap[:, :, 1:3], rasArrSwap[:, :, 3:]), axis=2)

    resized=skimage.transform.resize(rasArrFinal, (480,480,3))  
    image = np.expand_dims(resized, axis=0)
    
    
    # load json and create model
    json_file = open(model_fp, 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)
    loaded_model.load_weights(weights_fn)
    print("Loaded model from disk")
    
    # make predictions on the input image
    pred = loaded_model.predict(image)
    print('Side outputs')
    for imgs in pred:
        np.squeeze(imgs, axis=0)
        show(imgs)
    
    outArray=pred[0]
    outArray=np.squeeze(outArray, axis=0)
    outArray=np.squeeze(outArray, axis=2)
    imOut=Image.fromarray(outArray)
    imOut = imOut.resize((len(rasArrFinal[0]),len(rasArrFinal[:, 0])))
    final=np.array(imOut)
    print("final output")
    show(final)
    
    if Export_Image=='yes':
        def createImage(rawImage, array, imageName):
            raster=rasterio.open(rawImage)
            array=array[np.newaxis,...]
            array=array.astype(np.float32)
            kwargs=({'driver': raster.driver, 'dtype': 'float32', 'nodata': 0.0, 'width': raster.width, 
                     'height': raster.height, 'count':1,'crs': raster.crs, 'transform': raster.transform})
            
            with rasterio.open(imageName, 'w', **kwargs) as dest:
                dest.write(array)
        createImage(testImage,final, str(directory_name) + '/'+ str(Output_Image_Name) )
    else:
        print('Image not saved to file')