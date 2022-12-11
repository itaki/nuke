http://www.nukepedia.com/python/import/export/shufflelayers/finishdown?mjv=1
https://vimeo.com/496200256



Instrucciones
1.- Copiar el archivo shuffleLayers.py en la carpeta .nuke
2.- En el archivo menu.py incluir las siguientes líneas de código
import shuffleLayer
from shuffleLayers import newNode
from shuffleLayers import mylayerPanel


Intructions:
1.- Copy the file createNewshuffles.py in your .nuke folder
2.- In the menu.py file, add the following lines
import shuffleLayers
from shuffleLayers import newNode
from shuffleLayers import mylayerPanel

Una vez está instalada la herramienta
1.- Importa un material con un nodo Read
2.- En las propiedades del nodo, ir a la pestaña User
3.- Elige la opción "Create shuffles" si quieres crear un shuffle por cada
    capa que hay en el material
4.- Elige la opción "Select Layers" si no necesitas que se creen shuffles
    para todas las capas y quieres elegir que capas van a crear los shuffles  
Once the tool in installed

1.- Create a read node and import a material
2.- Go to User tab in the node properties
3.- Choose "Create Shuffles" option if you want to create one shuffle for
    each layer in the read node
4.- Choose "Select layers" option if you don't need shuffles for all Layers
    and you want to select which layers will create shuffle nodes
