import numpy as np
from numpy.lib import recfunctions as rfn
#import sys

def toUint(bytes):
        return int.from_bytes(bytes,"little",signed=False)

def fromUint(uint,byteamount):
    return int.to_bytes(uint,byteamount,byteorder='little',signed=False)



class Vertices:
    def __init__(self,file=None,parent=None) -> None:
        if file==None and parent==None:
            self.amount=0
            self.__store=[]
            self.coords=[]
            self.normals=[]
            self.texcoords=[]
        else:
            self.__initwithFile(file,parent)
    def __initwithFile(self,file,parent):
        if toUint(file.read(1))!=23:
            print("[Warning] file may contain errors {points marker wrong}")
        self.amount=toUint(file.read(2)) if parent.version<3 else toUint(file.read(4))
        if parent.udCorrect:               
            self.__store=[]
            zinit=0
            parent.kwak=np.dtype("<u2").type(parent.kwak)
            pcm65000=self.amount%65000
            for _ in range(self.amount):
                line=np.frombuffer(file.read(32),np.dtype("<f4")).copy()
                if parent.udata==0:
                    parent.kwak=304 if parent.f2 else 0 
                parent.kwak=((parent.kwak+zinit)*pcm65000)%8000
                floating_part=1
                for o in range(3):
                    floating_part*=line[o]-np.trunc(line[o])
                zinit=np.trunc((np.abs(floating_part)*600.)%256).astype(np.dtype("<u1"))
                copy_y=line[1]
                copy_x=line[0]
                if parent.kwak<1000:
                    line[1]=line[0]
                    line[0]=copy_y
                elif parent.kwak<3000:
                    line[0]=line[2]
                    line[2]=copy_x
                elif parent.kwak>7000:
                    line[1]=line[2]
                    line[2]=copy_y
                if parent.kwak&3==0:
                    line[3]*=-1
                copy_x=line[3]
                if parent.kwak%6==0:
                    line[4]*=-1
                if parent.kwak%7==0:
                    line[5]*=-1
                copy_y=line[5]
                if parent.kwak<600:
                    line[5]=line[4]
                    line[4]=copy_y
                else:
                    if parent.kwak<4501:
                        if parent.kwak>6500:
                            line[3]=line[5]
                            line[5]=copy_x
                    else:
                        line[3]=line[4]
                        line[4]=copy_x
                if parent.kwak%5==0:
                    line[6]-=(parent.kwak%100)**2/10000.
                if parent.kwak%3==0:
                    line[7]-=(parent.kwak%50)**2/2500.
                self.__store.append(line)
            self.__store=np.array(self.__store,dtype=np.dtype("<f4")).copy()
        else:
            self.__store=np.frombuffer(file.read(32*self.amount),np.dtype("<f4")).reshape(self.amount,8)
        self.coords=self.__store[:,:3].copy()
        self.normals=self.__store[:,3:6]
        self.texcoords=self.__store[:,6:8]
    def debugOut(self):
        print(np.c_[self.coords,self.normals,self.texcoords])
    def _writeTo(self,file,parent):
        file.write(fromUint(23,1))
        pcopy=np.c_[self.coords,self.normals,self.texcoords]
        file.write(fromUint(pcopy.shape[0],2 if parent.version<3 else 4))
        if parent.udCorrect:
            zinit=0
            parent.kwak=np.dtype("<u2").type(parent.kwak)
            pcm65000=self.amount%65000
            for line in pcopy:
                if parent.udata==0:
                    parent.kwak=304 if parent.f2 else 0 
                parent.kwak=((parent.kwak+zinit)*pcm65000)%8000
                copy_y=line[1]
                copy_x=line[0]
                if parent.kwak<1000:
                    line[1]=line[0]
                    line[0]=copy_y
                elif parent.kwak<3000:
                    line[0]=line[2]
                    line[2]=copy_x
                elif parent.kwak>7000:
                    line[1]=line[2]
                    line[2]=copy_y
                floating_part=1
                for o in range(3):
                    floating_part*=line[o]-np.trunc(line[o])
                zinit=np.trunc((np.abs(floating_part)*600.)%256).astype(np.dtype("<u1"))
                copy_x=line[3]
                copy_y=line[5]
                if parent.kwak<600:
                    line[5]=line[4]
                    line[4]=copy_y
                else:
                    if parent.kwak<4501:
                        if parent.kwak>6500:
                            line[3]=line[5]
                            line[5]=copy_x
                    else:
                        line[3]=line[4]
                        line[4]=copy_x
                if parent.kwak&3==0:
                    line[3]*=-1 
                if parent.kwak%6==0:
                    line[4]*=-1
                if parent.kwak%7==0:
                    line[5]*=-1
                if parent.kwak%5==0:
                    line[6]+=(parent.kwak%100)**2/10000.
                if parent.kwak%3==0:
                    line[7]+=(parent.kwak%50)**2/2500.
        file.write(pcopy.tobytes())

class Faces:
    def __init__(self,file=None,parent=None) -> None:
        if file==None and parent==None:
            self.amount=0
            self.__store=[]
            self.indices=[]
            self.texIndice=[]
        else:
            self.__initwithFile(file,parent)
    def __initwithFile(self,file,parent):
        if toUint(file.read(1))!=73:
            print("[Warning] file may contain errors {faces marker wrong}")
        self.amount=toUint(file.read(2)) if parent.version<3 else toUint(file.read(4))#or <3 must check later maybe
        if parent.f1:
            self.__store=rfn.structured_to_unstructured(np.frombuffer(file.read(14*self.amount),np.dtype("<u4,<u4,<u4,<u2")),dtype=np.dtype("<u4"))#.reshape(self.amount,4)
        else:
            self.__store=np.frombuffer(file.read(8*self.amount),np.dtype("<u2")).reshape(self.amount,4)
        self.indices=self.__store[:,:3]
        self.texIndice=self.__store[:,3:4]
    def debugOut(self):
        print(np.c_[self.indices,self.texIndice])
    def _writeTo(self,file,parent):
        file.write(fromUint(73,1))
        pcopy=np.c_[self.indices,self.texIndice]
        file.write(fromUint(pcopy.shape[0],2 if parent.version<3 else 4))
        file.write(rfn.unstructured_to_structured(pcopy,np.dtype("<u4,<u4,<u4,<u2") if parent.f1 else np.dtype("<u2,<u2,<u2,<u2")).tobytes())

class Materials:
    def __init__(self,file=None) -> None:
        if file==None:
            self.amount=0
            self.fdata=[]
            self.names=[]
        else:
            self.__initwithFile(file)
    def __initwithFile(self,file) -> None:
        if toUint(file.read(1))!=38:
            print("[Warning] file may contain errors {textures marker wrong}")
        self.amount=toUint(file.read(2))
        self.names=[]
        self.fdata=[]#(diff?)faceColor(RGBA)specularColor(RGB)emissiveColor(RGB)power(float)
        for _ in range(self.amount):
            self.fdata.append(np.frombuffer(file.read(44),np.dtype("<f4")))#11x4(float)
            self.names.append(file.read(toUint(file.read(1))).decode())
    def _writeTo(self,file):
        file.write(fromUint(38,1))
        file.write(fromUint(self.amount,2))
        for i in range(self.amount):
            file.write(self.fdata[i].tobytes())
            encodedString=self.names[i].encode()
            file.write(fromUint(len(encodedString),1))
            file.write(encodedString)
    
class Model:
    def __Matrix(self,file=None):
        if file==None:
            self.matrix=[]
        else:
            self.__MatrixwithFile(file)
    def __MatrixwithFile(self,file):
        if toUint(file.read(1))!=121:  
            print("[Warning] file may contain errors {matrix marker wrong}")
        self.matrix=np.frombuffer(file.read(64),np.dtype("<f4")).reshape(4,4)#4x4x4(float)

    def __Matrix_writeTo(self,file):
        file.write(fromUint(121,1))
        file.write(self.matrix.tobytes())

    def _update_fields(self):
        self.f1=True if self.flags&1==1 else False
        self.f2=True if self.flags&2==2 else False
        
        self.udCorrect= False if self.version<4 or self.udata==4294967295 else True
        if self.udCorrect:
            self.ud=self.udata+self.version-4
            self.kwak=(self.ud+381)%65000 if self.f2 else self.ud%65000
        else:
            self.ud=0
            self.kwak=0

    def __init__(self,filename=''):
        if filename=='':
            self.version=7
            self.flags=0
            self.udata=4294967295
            self.udCorrect=False
            self._update_fields()
            self.vertices=Vertices()
            self.faces=Faces()
            self.materials=Materials()
            self.__Matrix()
        else:
            self.__initwithFile(filename)

    def __initwithFile(self,filename):
         with open(filename,'rb')as f:
            if toUint(f.read(2))==6532:
                self.version=toUint(f.read(1))
                
                if self.version>2:
                    self.flags=np.frombuffer(f.read(1),np.dtype("<u1"))[0]
                    if self.version>3:
                        self.udata=np.frombuffer(f.read(4),np.dtype("<u4"))[0]
                    else:
                        self.udata=0
                else:
                    self.udata=0
                    self.flags=0
                
                self._update_fields()

                self.vertices=Vertices(f,self)#8x4(float)

                self.faces=Faces(f,self)#4x2(ushort)

                self.materials=Materials(f)
                
                self.__Matrix(f)
            else:
                print("[Warning] {o3d marker wrong}")
                self.__init__()

    def info(self):
        print("version:"+str(self.version))
        print(str(self.flags))
        print(str(self.udata))

    def pointsInfo(self):
        self.vertices.debugOut()

    def facesInfo(self):
        self.faces.debugOut()
        

    def matrixInfo(self):
        print(self.matrix)

    def texturesInfo(self):
        print("Textures:")
        for i in range(self.materials.amount):
            print("[{:3d}]".format(i),end=" ")
            print(self.materials.fdata[i],end=" ")
            print(self.materials.names[i])

    def extendedInfo(self):
        self.info()
        self.texturesInfo()
        self.pointsInfo()
        self.facesInfo()
        self.matrixInfo()

    def writeTo(self,filename,version,flag1:bool,flag2:bool,key):
        with open(filename,'wb')as file:
            file.write(fromUint(6532,2))
            file.write(fromUint(version,1))
            #protection
            if self.faces.amount>4294967295 and (flag1==False or version<3):
                if version<3:
                    version=3
                flag1=True
            self.version=version
            if self.version>2:
                self.flags=flag1&(flag2<<1)
                if self.version>3:
                    self.udata=key
                else:
                    self.udata=0
            else:
                self.udata=0
                self.flags=0
            self.f1=True if self.flags&1==1 else False
            self.f2=True if self.flags&2==2 else False
            
            self.udCorrect= False if self.version<4 or self.udata==4294967295 else True
            if self.udCorrect:
                self.ud=self.udata+self.version-4
                self.kwak=(self.ud+381)%65000 if self.f2 else self.ud%65000
            else:
                self.ud=0
                self.kwak=0

            if self.version>2:
                file.write(fromUint(self.flags,1))
                if self.version>3:
                    file.write(fromUint(self.udata,4))

            self.vertices._writeTo(file,self)
            self.faces._writeTo(file,self)
            self.materials._writeTo(file)
            self.__Matrix_writeTo(file)

    
def main():
    filename="D:\\Program Files (x86)\\OMSI 2.2.027\\Vehicles\\A3\\model\\A3_Rollband.o3d"
    #filename=sys.argv[1]
    #os.system('pause')
    obj=Model(filename)
    #obj.extendedInfo()
    #obj.texturesInfo()
    #obj.exportDirectXAsciiFrame(filename[:-4]+".x")

if __name__ == '__main__':
    main()
