from io import BufferedReader, BufferedWriter
import sys
import numpy as np
from numpy.lib import recfunctions as rfn
#import sys

def toUint(bytes):
        return int.from_bytes(bytes,"little",signed=False)

def fromUint(uint,byteamount):
    return int.to_bytes(uint,byteamount,byteorder='little',signed=False)



class Vertices:
    def __init__(self) -> None:
        self.amount=0
        #self.__store=[]
        self.coords=[]
        self.normals=[]
        self.texcoords=[]
    def loadFrom(self,file:BufferedReader,parent:'Model'):
        if toUint(file.read(1))!=23:
            print("[Warning] file may contain errors {points marker wrong}")
        self.amount=toUint(file.read(2)) if parent.version<3 else toUint(file.read(4))
        _store=np.frombuffer(file.read(32*self.amount),np.dtype("<f4")).reshape(self.amount,8)
        if parent.udCorrect:               
            zinit=0
            parent.kwak=np.dtype("<u2").type(parent.kwak)
            pcm65000=self.amount%65000
            for line in _store:
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
        self.coords=_store[:,:3].copy()
        self.normals=_store[:,3:6].copy()
        self.texcoords=_store[:,6:8].copy()
    def __str__(self):
        return str(np.c_[self.coords,self.normals,self.texcoords])
    def writeTo(self,file:BufferedWriter,parent:'Model'):
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

class Shapes:
    def __init__(self) -> None:
        self._shapes=[]
    def loadFrom(self,file:BufferedReader,parent:'Model'):
        if toUint(file.read(1))!=73:
            print("[Warning] file may contain errors {faces marker wrong}")
        self.amount=toUint(file.read(2)) if parent.version<3 else toUint(file.read(4))#or <3 must check later maybe
        if parent.f1:
            _store=rfn.structured_to_unstructured(np.frombuffer(file.read(14*self.amount),np.dtype("<u4,<u4,<u4,<u2")),dtype=np.dtype("<u4"))#.reshape(self.amount,4)
        else:
            _store=np.frombuffer(file.read(8*self.amount),np.dtype("<u2")).reshape(self.amount,4)
        #self.materialIndices=np.unique(_store[:,3])
        #self._shapes=[_store[_store[:,3]==i,:-1] for i in self.materialIndices]
        materialindices=np.unique(_store[:,3])
        self._shapes=[_store[_store[:,3]==i,:-1] for i in materialindices]
    def __getitem__(self,matIndice:int)->np.ndarray:
        #return self._shapes[self.materialIndices.index(key)]
        return self._shapes[matIndice]
    def __str__(self):
        _result=''
        for i in self._shapes:
            _result+=f'Shape[{self._shapes.index(i)}]:\n{i}\n'
        return _result
    def getFacesAmount(self):
        _result=0
        for _ in self._shapes:
            _result+=len(_)
        return _result
    def writeTo(self,file:BufferedWriter,parent:'Model'):
        file.write(fromUint(73,1))
        file.write(fromUint(self.getFacesAmount(),2 if parent.version<3 else 4))
        for _ in self._shapes:
            pcopy=np.c_[_,[self._shapes.index(_)]*len(_)]
            file.write(rfn.unstructured_to_structured(pcopy,np.dtype("<u4,<u4,<u4,<u2") if parent.f1 else np.dtype("<u2,<u2,<u2,<u2")).tobytes())

class Materials:
    def __init__(self) -> None:
        self.amount=0
        self.fdata:list[np.ndarray]=[]
        self.names:list[str]=[]
    def loadFrom(self,file:BufferedReader) -> None:
        if toUint(file.read(1))!=38:
            print("[Warning] file may contain errors {textures marker wrong}")
        self.amount=toUint(file.read(2))
        self.names=[]
        self.fdata=[]#(diff?)faceColor(RGBA)specularColor(RGB)emissiveColor(RGB)power(float)
        for _ in range(self.amount):
            self.fdata.append(np.frombuffer(file.read(44),np.dtype("<f4")))#11x4(float)
            self.names.append(file.read(toUint(file.read(1))).decode(encoding=sys.getdefaultencoding()))
    def writeTo(self,file:BufferedWriter):
        file.write(fromUint(38,1))
        file.write(fromUint(self.amount,2))
        for i in range(self.amount):
            file.write(self.fdata[i].tobytes())
            encodedString=self.names[i].encode(encoding=sys.getdefaultencoding())
            file.write(fromUint(len(encodedString),1))
            file.write(encodedString)
    def __str__(self):
        _result=""
        for i in range(self.amount):
            fd=self.fdata[i]
            _result+=f"Material[{i}]:\n\tface color: {fd[:4]}\n\tspecular color: {fd[4:7]}\n\temissive color: {fd[7:10]}\n\tpower: {fd[10]}\n\ttexture: {self.names[i]}\n"
        return _result
class Matrix:
    def __init__(self) -> None:
        self.data=[]
    def writeTo(self,file:BufferedWriter):
        if self.data!=[]:
            file.write(fromUint(121,1))
            file.write(self.data.tobytes())
    def loadFrom(self,file:BufferedReader):
        if toUint(file.read(1))!=121:  
            print("[Warning] file may contain errors {matrix marker wrong}")
        self.data=np.frombuffer(file.read(64),np.dtype("<f4")).reshape(4,4)#4x4x(4)(float)
    def __str__(self) -> str:
        return str(self.data)

class Model:
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

    def __init__(self):
        self.version=7
        self.flags=0
        self.udata=4294967295
        self._update_fields()
        self.vertices=Vertices()
        self.shapes=Shapes()
        self.materials=Materials()
        self.matrix=Matrix()

    def loadFromFile(self,filename:str):
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

                self.vertices.loadFrom(f,self)#8x4(float)

                self.shapes.loadFrom(f,self)#4x2(ushort)

                self.materials.loadFrom(f)
                
                self.matrix.loadFrom(f)
            else:
                print("[Warning] {o3d marker wrong}")
                self.__init__()

    def info(self):
        print("version:"+str(self.version))
        if self.version>2:
            print(f"flags:{self.flags:08b}")
            if self.version>3:
                print(f"key:0x{self.udata:016X}")

    def extendedInfo(self):
        self.info()
        print(self.materials)
        print(self.vertices)
        print(self.shapes)
        print(self.matrix)

    def writeTo(self,filename,version,flag1:bool,flag2:bool,key):
        with open(filename,'wb')as file:
            file.write(fromUint(6532,2))
            file.write(fromUint(version,1))
            #protection
            if self.shapes.getFacesAmount()>4294967295 and (flag1==False or version<3):
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

            self.vertices.writeTo(file,self)
            self.shapes.writeTo(file,self)
            self.materials.writeTo(file)
            self.matrix.writeTo(file)

    
def main():
    filename="D:\\Program Files (x86)\\OMSI 2.2.027\\Vehicles\\A3\\model\\A3_Rollband.o3d"
    #filename=sys.argv[1]
    #os.system('pause')
    obj=Model()
    obj.loadFromFile(filename)
    obj.extendedInfo()
    #obj.extendedInfo()
    #obj.texturesInfo()
    #obj.exportDirectXAsciiFrame(filename[:-4]+".x")

if __name__ == '__main__':
    main()
