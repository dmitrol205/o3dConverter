import os
import tokenize
import numpy as np
from o3dModel import Model

class O3dConvWaveFront(Model):
    @staticmethod
    def transform(obj:Model):
        if isinstance(obj,Model):
            obj.__class__=O3dConvWaveFront
    def exportWaveFront(self,filename):
        matfilename=os.path.splitext(filename)[0]+'.mtl'
        with open(matfilename,'w')as file:
            for i in range(self.materials.amount):
                file.write('newmtl Material_'+str(i+1))
                cm=self.materials.fdata[i]
                file.write(f'\nKa {1:.6f} {1:.6f} {1:.6f}')
                file.write(f'\nKd {cm[0]:.6f} {cm[1]:.6f} {cm[2]:.6f}')
                file.write(f'\nKs {cm[4]:.6f} {cm[5]:.6f} {cm[6]:.6f}')
                file.write(f'\nKe {cm[7]:.6f} {cm[8]:.6f} {cm[9]:.6f}')
                file.write('\nillum 2')
                file.write(f'\nd {cm[3]:.6f}')
                file.write(f'\nNs {cm[10]:.6f}')
                file.write(f'\nmap_Kd {self.materials.names[i]}')
                file.write('\n\n')
        with open(filename,'w')as file:
            file.write('mtllib ') 
            file.write(os.path.split(matfilename)[1])
            file.write('\n\ng Object')
            for i in self.vertices.coords:
                file.write(f'\nv {-i[0]:.6f} {i[1]:.6f} {i[2]:.6f}')
            for i in self.vertices.normals:
                file.write(f'\nvn {i[0]:.6f} {i[1]:.6f} {i[2]:.6f}')
            for i in self.vertices.texcoords:
                file.write(f'\nvt {i[0]:.6f} {1-i[1]:.6f}')
            faces=np.c_[self.faces.indices+1,self.faces.materialIndice]#.astype(np.dtype('<u4'))
            for i in range(self.materials.amount):
                file.write('\nusemtl Material_'+str(i+1))
                for o in faces:
                    if o[3]==i:
                        file.write(f'\nf {o[1]}/{o[1]}/{o[1]} {o[0]}/{o[0]}/{o[0]} {o[2]}/{o[2]}/{o[2]}')
                        #file.write(f'\nf {o[2]}/{o[2]}/{o[2]} {o[1]}/{o[1]}/{o[1]} {o[0]}/{o[0]}/{o[0]}')
                        #file.write(f'\nf {o[0]}/{o[0]}/{o[0]} {o[1]}/{o[1]}/{o[1]} {o[2]}/{o[2]}/{o[2]}')
                        #file.write(f'\nf {o[0]} {o[1]} {o[2]}')

    def importmtl(self,filename):
        mats={}
        with open(filename,'rb')as file:
            tokens=tokenize.tokenize(file.readline)
            token=tokens.__next__()
            if not(token.type==59 and token.string=='utf-8'):
                print('expected utf-8 but '+token.string+' present')
                return False
            def nn():
                while True:
                    token=tokens.__next__()
                    if token.exact_type==4 or token.exact_type==58 or token.exact_type==0:
                        break 
                return True                   
            def vn(varname:str):
                token=tokens.__next__()
                if token.type!=1:
                    print(f'expected {varname} but '+token.string+' present of type '+str(token.type)+" "+str(token.exact_type))
                    return False
                return token.string
            def fc(cnt:int,notint:bool=True,negative:bool=False):
                numa=[]
                for _ in range(cnt):
                    num=tokens.__next__()
                    if negative and num.exact_type==15:
                        sign=-1
                        num=tokens.__next__()
                    else:
                        sign=1
                    if num.exact_type!=2:
                        print('expected <number> but '+token.string+' present of type '+str(token.type)+" "+str(token.exact_type))
                        return False
                    if notint:
                        num=float(num.string)
                    else:
                        num=int(num.string)
                    num*=sign
                    numa.append(num)
                return numa

            colors={}

            def uc():
                nonlocal colors
                if colors!={}:
                    if 'n' not in colors:
                        print('missing materialTexture')
                        return False
                    if 'e' not in colors:
                        print('missing emissive color')
                        return False
                    if 's' not in colors:
                        print('missing specular color')
                        return False
                    if 'd' not in colors:
                        print('missing diffuse color')
                        return False
                    if 'o' not in colors:
                        print('missing opacity (d)')
                        return False
                    if 'i' not in colors:
                        print('missing power (Ns)')
                        return False
                    self.materials.names.append(colors['n'])
                    __arr=colors['d']
                    __arr.extend(colors['o'])
                    __arr.extend(colors['s'])
                    __arr.extend(colors['e'])
                    __arr.extend(colors['i'])
                    self.materials.fdata.append(__arr)
                    colors={}
                return True

            def nm()->bool:
                matName=vn("<materialName>")
                if not matName:return False
                mats[matName]=self.materials.amount
                if not uc():
                    print('current material is',{v:k for k,v in mats.items()}[self.materials.amount-1])  
                    return False
                nn()
                self.materials.amount+=1
                return True
            def kk(key:str,num:int)->bool:
                nonlocal colors
                numa=fc(num)
                if not numa:return False
                colors[key]=numa
                nn()
                return True
            def kd()->bool:
                if not kk('d',3):return False 
                return True
            def ks()->bool:
                if not kk('s',3):return False 
                return True
            def ke()->bool:
                if not kk('e',3):return False 
                return True
            def df()->bool:
                if not kk('o',1):return False 
                return True
            def ns()->bool:
                if not kk('i',1):return False 
                return True
            def mk()->bool:
                nonlocal colors
                __name=''
                while True:
                    i=tokens.__next__()
                    if i.exact_type==4 or i.exact_type==58:
                        break
                    __name+=i.string
                colors['n']=__name
                return True
            strucs={
                'newmtl':nm,
                'Ka':nn,
                'Kd':kd,
                'Ks':ks,
                'Ke':ke,
                'd':df,
                'Ns':ns,
                'illum':nn,
                'map_Kd':mk,
                'Ni':nn
            }
            for i in tokens:
                if i.type==1:
                    if i.string in strucs:
                        if not strucs[i.string]():
                            print("failed parsing "+i.string)
                            return False
                    else:
                        print(i.type,i.exact_type,"'"+i.string+"'")
                elif i.exact_type==57:
                    nn()
                elif i.type==4 or i.type==58:
                    pass
                else:
                    print(i.type,i.exact_type,"'"+i.string+"'")
            if not uc():
                print('current material is',{v:k for k,v in mats.items()}[self.materials.amount-1]) 
                return False
            self.materials.fdata=np.array(self.materials.fdata,dtype=np.dtype('<f4')).reshape(self.materials.amount,11).copy()
        return mats
            
    def importWaveFront(self,filename):
        with open(filename,'rb')as file:
            tokens=tokenize.tokenize(file.readline)
            token=tokens.__next__()
            if not(token.type==59 and token.string=='utf-8'):
                print('expected utf-8 but '+token.string+' present')
                return False
            def nt():
                token=tokens.__next__()
                while token.exact_type==4 or token.exact_type==58:
                    token=tokens.__next__()
                return token
            matnames={}
            currentmaterial=-1
            adv_face=[]
            symbols={
                ';':13,'{':25,'}':26,',':12,'-':15,'#':57,'/':17
            }
            def nn():
                while True:
                    token=tokens.__next__()
                    if token.exact_type==4 or token.exact_type==58 or token.exact_type==0:
                        break  
                return True                  
            strucs={}#stub for vf
            def vn(varname:str):
                token=tokens.__next__()
                if token.type!=1:
                    print(f'expected {varname} but '+token.string+' present of type '+str(token.type)+" "+str(token.exact_type))
                    return False
                return token.string
            def fc(cnt:int,notint:bool=True,negative:bool=False):
                numa=[]
                for _ in range(cnt):
                    num=tokens.__next__()
                    if negative and num.exact_type==15:
                        sign=-1
                        num=tokens.__next__()
                    else:
                        sign=1
                    if num.exact_type!=2:
                        print('expected <number> but '+token.string+' present of type '+str(token.type)+" "+str(token.exact_type))
                        return False
                    if notint:
                        num=float(num.string)
                    else:
                        num=int(num.string)
                    num*=sign
                    numa.append(num)
                return numa
           
                while True:
                    token=nt()
                    if token.exact_type==26:
                        return True
                    if token.exact_type==1:
                        if token.string in strucs:
                            if not strucs[token.string]():
                                print("failed parsing "+token.string)
                                return False
                            else:
                                continue
                        else:
                            print('unknown token present '+token.string)
                            return False
                    else:
                        print('expected <structName> but '+token.string+' present of type '+str(token.type)+" "+str(token.exact_type))
                        return False

            def ml()->bool:
                nonlocal matnames
                __name=''
                while True:
                    i=tokens.__next__()
                    if i.exact_type==4 or i.exact_type==58:
                        break
                    __name+=i.string
                mtlfilename=__name
                if not mtlfilename:return False
                #nn()
                matnames=self.importmtl(os.path.split(filename)[0]+'/'+mtlfilename)
                if not matnames:
                    print('failed importing materials from',mtlfilename)
                    return False
                return True
            def vc()->bool:
                i=fc(3,True,True)
                if not i:return False
                self.vertices.coords.append(i)
                nn()
                return True
            def vt()->bool:
                i=fc(2,True,True)
                if not i:return False
                self.vertices.texcoords.append(i)
                nn()
                return True
            def nv()->bool:
                i=fc(3,True,True)
                if not i:return False
                self.vertices.normals.append(i)
                nn()
                return True
            def um()->bool:
                nonlocal currentmaterial
                i=vn('<materialName>')
                if not i:return False
                currentmaterial=matnames[i]
                nn()
                return True
            def fa()->bool:
                nonlocal adv_face
                o=[]
                u=[]
                i=tokens.__next__()
                for _ in range(3):
                    if i.exact_type!=2:
                        print('expected <vertexIndex>  but '+token.string+' present of type '+str(token.type)+" "+str(token.exact_type))
                        return False
                    o.append(int(i.string))
                    u.append(int(i.string))
                    i=tokens.__next__()
                    if i.exact_type==2:
                        u.append(1)
                        u.append(1)
                        continue
                    elif i.exact_type!=17:
                        print('expected <vertexIndex> or / but '+token.string+' present of type '+str(token.type)+" "+str(token.exact_type))
                        return False
                    i=tokens.__next__()
                    if i.exact_type==17:
                        i=tokens.__next__()
                        if i.exact_type==2:
                            u.append(1)
                            u.append(int(i.string))
                            i=tokens.__next__()
                            continue
                        else:
                            print('expected <normalIndex> but '+token.string+' present of type '+str(token.type)+" "+str(token.exact_type))
                            return False
                    elif i.exact_type!=2:
                        print('expected <uvIndex> or / but '+token.string+' present of type '+str(token.type)+" "+str(token.exact_type))
                        return False
                    u.append(int(i.string))
                    i=tokens.__next__()
                    if i.exact_type==17:
                        i=tokens.__next__()
                        if i.exact_type==2:
                            u.append(int(i.string))
                            i=tokens.__next__()
                            continue
                        else:
                            print('expected <normalIndex> but '+token.string+' present of type '+str(token.type)+" "+str(token.exact_type))
                            return False
                    print('expected / but '+token.string+' present of type '+str(token.type)+" "+str(token.exact_type))
                    return False
                adv_face.append(u)
                self.faces.indices.append(o)
                self.faces.materialIndice.append(currentmaterial)
                if not( i.exact_type==4 or i.exact_type==58 or i.exact_type==0):nn()
                return True
            strucs={
                'mtllib':ml,
                'g':nn,
                'v':vc,
                'vt':vt,
                'vn':nv,
                'usemtl':um,
                'f':fa,
                'o':nn,
                's':nn,
            }
            for i in tokens:
                if i.type==1:
                    if i.string in strucs:
                        if not strucs[i.string]():
                            print("failed parsing "+i.string)
                            return False
                    else:
                        print(i.type,i.exact_type,"'"+i.string+"'")
                elif i.exact_type==57:
                    nn()
                elif i.type==4 or i.type==58:
                    pass
                else:
                    print(i.type,i.exact_type,"'"+i.string+"'")
            self.vertices.amount=len(self.vertices.coords)
            self.faces.amount=len(self.faces.indices)
            if self.vertices.normals==[]:
                self.vertices.normals=np.c_[np.ones([self.vertices.amount,1]),np.zeros([self.vertices.amount,2])].astype(np.dtype('<f4'))
            if self.vertices.texcoords==[]:
                self.vertices.texcoords=np.zeros((self.vertices.amount,2)).astype(np.dtype('<f4'))
            self.vertices.coords=np.array(self.vertices.coords,dtype=np.dtype('<f4'))
            self.vertices.normals=np.array(self.vertices.normals,dtype=np.dtype('<f4'))
            self.vertices.texcoords=np.array(self.vertices.texcoords,dtype=np.dtype('<f4'))
            if not(self.vertices.amount==len(self.vertices.texcoords) and self.vertices.amount==len(self.vertices.normals)):
                adv_face=np.array(adv_face,dtype=np.dtype('<u4'))-1
                nc=self.vertices.normals
                tc=self.vertices.texcoords
                self.vertices.normals=np.zeros_like(self.vertices.coords)
                self.vertices.texcoords=np.zeros((len(self.vertices.coords),2),dtype=self.vertices.coords.dtype)
                adv_face=adv_face.reshape((-1,3))
                for i in adv_face:
                    self.vertices.normals[i[0]]=nc[i[2]]
                    self.vertices.texcoords[i[0]]=tc[i[1]]
            self.faces.indices=np.array(self.faces.indices,dtype=np.dtype('<u4'))
            self.faces.materialIndice=np.array(self.faces.materialIndice,dtype=np.dtype('<u4')).reshape((self.faces.amount,1))
            self.faces.indices-=1
            #self.points.coords=np.c_[self.points.coords[:,0],self.points.coords[:,2],self.points.coords[:,1]].copy()
            #self.points.normals=np.c_[self.points.normals[:,0],self.points.normals[:,2],self.points.normals[:,1]].copy()
            self.vertices.coords[:0]*=-1
            self.vertices.texcoords[:,1]=1.-self.vertices.texcoords[:,1]
            self.faces.indices=np.c_[self.faces.indices[:,1],self.faces.indices[:,0],self.faces.indices[:,2]].copy()
            self.vertices.__store=np.c_[self.vertices.coords,self.vertices.normals,self.vertices.texcoords].astype(np.dtype('<f4'))
            self.faces.__store=np.c_[self.faces.indices,self.faces.materialIndice].astype(np.dtype('<u4'))
            if self.vertices.amount!=len(self.vertices.__store):
                print("not enough vertex coords")
                return False
            if self.matrix==[]:
                self.matrix=np.array([[1.,0.,0.,0.],[0.,1.,0.,0.],[0.,0.,1.,0.],[0.,0.,0.,1.]],dtype=np.dtype('<f4'))
        return True