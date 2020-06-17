import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton,QLabel,QFileDialog,QHBoxLayout
                            ,QDesktopWidget,QVBoxLayout, QSizePolicy)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import cv2
from PIL import Image
import numpy as np
import math
import os
if not os.path.exists('./temp'):
    os.mkdir('./temp')
def Psnr(img1, img2):
    img1=cv2.imread(img1)
    img2=cv2.imread(img2)
    mse = np.mean( (img1 - img2) ** 2 )
    if mse == 0:
        return 100
    PIXEL_MAX = 255.0
    return 20 * math.log10(PIXEL_MAX / math.sqrt(mse))

class PlotCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        #self.axes = fig.add_subplot(111)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        #self.plot()


    def plot(self,x,y,color='',title='plot'):
        ax = self.figure.add_subplot(111)
        ax.bar(x,y,color=color)
        ax.set_title(title)
        self.draw()


class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'puree_no_dedo'
        sizeObject =QDesktopWidget().screenGeometry(-1)
        self.left = 45
        self.top = 100
        self.width = sizeObject.width()-800
        self.height = sizeObject.height()-400
        self.loc1=''
        self.initUI()
        
        
#image convert
    def black_and_white(self,input_image_path,output_image_path='./temp/in_wm.png'):
        self.size=128
        dim = (self.size,self.size)
        img = cv2.imread(input_image_path)
        img= cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _,img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
        cv2.imwrite(output_image_path,img)
        self.in_wm=np.array(img)
        self.wm1.setPixmap(QPixmap('./temp/in_wm.png'))
        self.in_img(address='1')
        self.image3.setPixmap(QPixmap('./temp/embeded.png').scaled(280,180, Qt.IgnoreAspectRatio, Qt.FastTransformation))
     
#image input
    def in_img(self,address=''):
        if(address==''):
            im = Image.open(self.loc1)
            self.image1.setPixmap(QPixmap(self.loc1).scaled(640, 360, Qt.IgnoreAspectRatio, Qt.FastTransformation))
            pix = im.load()
            height,width=im.size # Get the width and hight of the image for iterating over
            temp=np.zeros((width,height))
            #calculating frequency of grayscale value in the image and ploting bar graph
            frequency=list()
            col=list()
            x=list()
            for i in range(256):
                frequency.append(0)
                x.append(i)
                col.append('lime')
            for i in range(height):
                for j in range(width):
                    frequency[pix[i,j]]+=1
            
            #finding peak point and minimum point
            maxp=0
            for i in range(256):
                if(frequency[i]>frequency[maxp]):
                    maxp=i
            if(maxp==0):
                maxp2=1
            else:
                maxp2=0
            for i in range(256):
                if(frequency[i]>frequency[maxp2] and frequency[i]<frequency[maxp]):
                    maxp2=i
            print(maxp,maxp2)
            if(maxp>maxp2): 
                for i in range(maxp2,maxp+1):
                    col[i]='cyan'
            else:
                for i in range(maxp,maxp2+1):
                    col[i]='cyan'
            self.g1.plot(x=x,y=frequency,title='initial img',color=col)
            #finding and storing coordinates of minimum value
            self.cor=list()
            for i in range(height):
                for j in range(width):
                    if(pix[i,j]==maxp2):
                       self.cor.append([i,j])
            
            
            #histogram shifting
            self.flag=0
            if(maxp-maxp2==1):
                self.flag=1
                maxp2-=1
            elif(maxp-maxp2==-1):
                maxp2+=1
                self.flag=-1
            
            if(maxp<maxp2):
                for i in range(height):
                    for j in range(width):
                        if(pix[i,j]<maxp2 and pix[i,j]>maxp):
                            temp[j][i]=255
                            pix[i,j]+=1
            else:
                for i in range(height):
                    for j in range(width):
                        if(pix[i,j]>maxp2 and pix[i,j]<maxp):
                            temp[j][i]=255
                            pix[i,j]-=1
            maxp2+=self.flag
        
                        
            #recalculating frequency
            for i in range(256):
                frequency[i]=0
            for i in range(height):
                for j in range(width):
                    frequency[pix[i,j]]+=1
            
            
            self.maxp=maxp
            self.maxp2=maxp2
            
            #saving the image
            cv2.imwrite('./temp/shift.png',temp)
            self.g2.plot(x=x,y=frequency,color='lime',title=('after histogram shifting\n'+'psnr='+str(round(Psnr(self.loc1,'./temp/shift.png'),4))))
            self.image2.setPixmap(QPixmap('./temp/shift.png').scaled(640, 360, Qt.IgnoreAspectRatio, Qt.FastTransformation))
        else:
            im = Image.open(self.loc1)
            pix = im.load()
            height,width=im.size # Get the width and hight of the image for iterating over
            
            maxp=self.maxp
            maxp2=self.maxp2
            bstring=''
            for i in range(self.size):
                for j in range(self.size):
                    if(self.in_wm[i][j]):
                        bstring+='1'
                    else:
                        bstring+='0'
         
            
            #histogram shifting
            maxp2-=self.flag
            if(maxp<maxp2):
                for i in range(height):
                    for j in range(width):
                        if(pix[i,j]<maxp2 and pix[i,j]>maxp):
                            pix[i,j]+=1
            else:
                for i in range(height):
                    for j in range(width):
                        if(pix[i,j]>maxp2 and pix[i,j]<maxp):
                            pix[i,j]-=1
            maxp2+=self.flag
                
            #writing binary data into image
            k=0
            for i in range(height):
                for j in range(width):
                    if(pix[i,j]==maxp and k<len(bstring)):
                        if(bstring[k]=='1' and maxp2>maxp):
                            pix[i,j]+=1
                        elif(bstring[k]=='1' and maxp2<maxp):
                            pix[i,j]-=1
                        k+=1
                        
            #recalculating frequency
            frequency=list()
            x=list()
            for i in range(256):
                frequency.append(0)
                x.append(i)
            for i in range(height):
                for j in range(width):
                    frequency[pix[i,j]]+=1
            
            
            self.maxp=maxp
            self.maxp2=maxp2            
            
            
            #saving the image
            im.save('./temp/embeded.png')
            
            psnr=cv2.PSNR(cv2.imread(self.loc1),cv2.imread('./temp/embeded.png'))
            psnr=round(psnr,4)
            self.g3.plot(x=x,y=frequency,color='lime',title=('after writing data    '+'psnr='+str(round(Psnr(self.loc1,'./temp/embeded.png'),4))))
        
#image output
    def out_img(self,address='./temp/embeded.png'):
        im = Image.open(address)
        pix = im.load()
        height,width=im.size # Get the width and hight of the image for iterating over
        
        #extracting data
        image=np.zeros((self.size,self.size))
        k1=0
        k2=0
        flag=False
        for i in range(height):
            for j in range(width):
                if(k2==self.size):
                    k1+=1
                    k2=0
                if(k1==self.size):
                    flag=True
                    break
                if(pix[i,j]==self.maxp):
                    k2+=1
                elif(pix[i,j]==self.maxp-1 and self.maxp2<self.maxp):
                    image[k1,k2]=255
                    k2+=1
                elif(pix[i,j]==self.maxp+1 and self.maxp2>self.maxp):
                    image[k1,k2]=255
                    k2+=1
            if(flag):
                break
        cv2.imwrite('./temp/ex_wm.png',image)
                    
        
        #histogram shifting
        self.maxp2-=self.flag
        if(self.maxp<self.maxp2):
            for i in range(height):
                for j in range(width):
                    if(pix[i,j]<=self.maxp2 and pix[i,j]>self.maxp):
                        pix[i,j]-=1
        else:
            for i in range(height):
                for j in range(width):
                    if(pix[i,j]>=self.maxp2 and pix[i,j]<self.maxp):
                        pix[i,j]+=1
        i=0
        self.maxp2+=self.flag
        for i in self.cor:
            pix[i[0],i[1]]=self.maxp2
        
        frequency=list()
        x=list()
        for i in range(256):
            frequency.append(0)
            x.append(i)
        for i in range(height):
            for j in range(width):
                frequency[pix[i,j]]+=1
                
        #saving the image
        im.save('./temp/restored.png')
        
        self.g4.plot(x=x,y=frequency,color='lime',title=('after restoration    '+'psnr='+str(round(Psnr(self.loc1,'./temp/restored.png'),4))))
        
#event handeling
    def on_click1(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', './')
        
        if fname[0]:
            self.loc1=fname[0]
            img=cv2.imread(self.loc1)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            self.loc1='./temp/gray_img.png'
            cv2.imwrite(self.loc1,img)
            self.in_img()
            
            
    def on_click2(self):
        if self.loc1!='':
            fname = QFileDialog.getOpenFileName(self, 'Open file', './')
            
            if fname[0]:
                self.black_and_white(input_image_path=fname[0])
                self.out_img()
                self.wm2.setPixmap(QPixmap('./temp/ex_wm.png'))
                self.image4.setPixmap(QPixmap('./temp/restored.png').scaled(280, 180, Qt.IgnoreAspectRatio, Qt.FastTransformation))
            
            
#driver function            
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        
        #layout
        mbox = QHBoxLayout()
        vbox1=QVBoxLayout()
        vbox2=QVBoxLayout()
        vbox3=QVBoxLayout()
        hbox1=QHBoxLayout()
        vbox31=QVBoxLayout()
        vbox32=QVBoxLayout()
        
        #for vbox1
        open_file1 = QPushButton('open file', self)
        self.image1=QLabel('')
        open_file1.clicked.connect(self.on_click1)
        self.g1 = PlotCanvas(self)
        
        #for vbox2
        title2=QLabel('\nimage difference')
        self.image2=QLabel('')
        self.g2 = PlotCanvas(self)
        
        #for vbox3
        open_file2= QPushButton('open file', self)
        title3_1=QLabel('embedding watermark')
        title3_2=QLabel('\nextracting watermark')
        self.wm1=QLabel('')
        self.image3=QLabel('')
        self.wm2=QLabel('')
        self.image4=QLabel('')
        open_file2.clicked.connect(self.on_click2)
        self.g3=PlotCanvas(self)
        self.g4=PlotCanvas(self)

        
    #layout management
        #for vbox1
        vbox1.addWidget(open_file1)
        vbox1.addWidget(self.image1)
        vbox1.addWidget(self.g1)
        #for vbox2
        vbox2.addWidget(title2)
        vbox2.addWidget(self.image2)
        vbox2.addWidget(self.g2)
        #for vbox3
        vbox31.addWidget(open_file2)
        vbox31.addWidget(title3_1)
        vbox31.addWidget(self.wm1)
        vbox31.addWidget(self.image3)
        vbox32.addWidget(title3_2)
        vbox32.addWidget(self.wm2)
        vbox32.addWidget(self.image4)
        hbox1.addLayout(vbox31)
        hbox1.addLayout(vbox32)
        vbox3.addLayout(hbox1)
        vbox3.addWidget(self.g3)
        vbox3.addWidget(self.g4)
        
        
        mbox.addLayout(vbox1)
        mbox.addLayout(vbox2)
        mbox.addLayout(vbox3)
        self.setLayout(mbox)
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())