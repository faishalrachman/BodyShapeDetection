import numpy as np
import io
from PIL import Image
from libs.mobilenetv2_model import load_model
from io import BytesIO, StringIO
import matplotlib.pyplot as plt
import base64

body_string = {
    "H" : {
      "title" : "Rectangle",
      "desc" : "Choose A-line skirts with ruffled and layered tops. Dresses that add definition to your bottom and necklines that add weight to the upper body. Sleeveless, strapless and sweetheart lines are your thing. Blazers, long jackets and capes add the much-needed drama here."
    },
    "X" : {
      "title" : "Hourglass",
      "desc" : "Dresses that cinch at the waist will be your best fit. V-necks or plunge necklines and sweetheart necklines help you flaunt your upper body. To show off your waistline, go with a belt at your natural waistline or just below the belly button. A-line dresses or similar cuts take care of working on the lower part of the body and of course, body-hugging dresses are your thing, because, why not?"
    },
    "O" : {
      "title" : "Apple",
      "desc" : "Find clothes that suit your body type by looking to a-line or empire cut blouses and dresses. Wear printed dresses or patterned jackets that add a layer to shift the focus. Monochrome looks, dark colors, full or 3/4th sleeves dresses and flowy tops will help. You could also wear flared bottoms; palazzos etc. to create a balance. Also, since your shoulders are broad and you might already have a bigger bustline, ensure you wear the right bra."
    },
    "A" : {
      "title" : "Triangle",
      "desc" : "Find clothes that suit your body type by looking to wide legged pants, A-line skirts or dresses with patterned or ruffled tops that add definition to the upper body. Skinny jeans with loose tops help create an hourglass illusion and high waist jeans show off the smallest part of your waist. Crop tops, sweetheart, v-necks, scoop or boat necks will balance your bottom out."
    },
    "V" : {
      "title" : "Inverted Triangle",
      "desc" : "Since your hips are much narrower than your shoulders, pencil skirts or skinny jeans with any top will look great. V-neck lines work well and create an illusion of narrow shoulders, so this should be your go-to neckline."
    }
}

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

def getShapeFromImage(file_path, MODEL):
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
  bentuk_badan = body_shape_measurement(lebar_bahu,lebar_pinggang,lebar_panggul,toleransi)

  newByte = BytesIO()
  # buffer_image.save(newByte, format="JPEG")

  plt.ioff()
  plt.imshow(seg_map)
  plt.imshow(resized_image, alpha=0.5)
  plt.savefig(newByte, format="JPEG")
  plt.close()
  newByte.seek(0)
  encoded_string = base64.b64encode(newByte.getvalue()).decode("utf-8")
  
  body_code = body_string[bentuk_badan]
  #Metadata
  output = {
    "bahu" : lebar_bahu,
    "pinggang": lebar_pinggang,
    "panggul": lebar_panggul,
    "bentuk_badan" : body_code["title"],
    "saran" : body_code["desc"],
    "image_encoded" : encoded_string
  }
  #Return the body shape measurement (H, A, X, O, V)
  return output