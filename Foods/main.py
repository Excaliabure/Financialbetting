import os
from os.path import join
import glob

from PIL import Image
from pytesseract import pytesseract



PATH = join('\\'.join(__file__.split("\\")[:-1]))
recipts = join(PATH, "Recipt_Images")



pytesseract.tesseract_cmd = 