import numpy as np
import io
from PIL import Image
from libs.mobilenetv2_model import load_model

def is_equal(a, b, tol_rate):
  return abs(a-b) < tol_rate

def is_smaller(a, b, tol_rate):
  return abs(a-b) < tol_rate

def is_bigger(a, b, tol_rate):
  return abs(a-b) < tol_rate

def pixel_to_cm(pixel, height_pixel, height_cm):
  return pixel * height_cm / height_pixel
  
def titikAtas(seg_map, code):
  y, x = seg_map.shape
  tengah = x // 2
  for i in range(y):
    if (seg_map[i][tengah] == code):
      return (tengah, i)
  return -1
def titikBawah(seg_map, code):
  y, x = seg_map.shape
  tengah = x // 2
  for i in range(y-1, 0, -1):
    for j in range(x):
      if (seg_map[i][j] == code):
        return (tengah, i)
  return -1
  
def cariHorizontal(image, code):
  # cari depan
  depan = 0
  tengah = len(image)//2
  for i in range(tengah, 0, -1):
    if (image[i] != code):
        depan = i
        break
  for i in range(tengah, len(image)):
    if (image[i] != code):
        belakang = i
        break
  return (depan, belakang)

def body_shape_measurement(ba, pi, pa, tol):
  if (is_equal(ba,pa,tol)):
    if (is_equal(ba, pi, tol)):
      return "H"
    elif (ba > pi and ba > pi+5):
      return "X"
    elif (ba > pi):
      return "H"
    else: # (ba < pi)
      return "O"
  elif (ba < pa) :
    return "A"
  else:  # (ba > pa)
    return "V"


def getShapeFromImage(file_path):
  #Load Segmentation Model
  MODEL = load_model()
  #Open Image File
  f = open(file_path,"rb")
  jpeg_str = f.read()
  #Convert file to image on buffer
  original_im = Image.open(BytesIO(jpeg_str))
  #Run image segmentation
  resized_image, seg_map = MODEL.run(original_im)
  #Crop image above head and under feet
  code_person = 15
  head = titikAtas(seg_map,code_person)
  bottom = titikBawah(seg_map,code_person)
  new_image = seg_map[head[1]:bottom[1],:]
  #Define vertical segmentation line
  jumlah_garis = 19
  pembagian = new_image.shape[0] // jumlah_garis
  #Find Distances of the segmentation line
  distances = []
  titik_titik = []
  for i in range(1, jumlah_garis+1):
    titik = i * pembagian
    x1 = cariHorizontal(new_image[titik, :], code_person)
    x2 = (titik, titik)
    titik_titik.append([x1, x2[0]])
    distances.append(x1[1]-x1[0])
  #Define bahu, pinggang and panggul
  titik_bahu = 4
  titik_pinggang = 8
  titik_panggul = 10
  toleransi = 2 #centimeters
  lebar_bahu = distances[titik_bahu]
  lebar_pinggang = distances[titik_pinggang]
  lebar_panggul = distances[titik_panggul]
  #Return the body shape measurement (H, A, X, O, V)
  return body_shape_measurement(lebar_bahu,lebar_pinggang,lebar_panggul,toleransi)