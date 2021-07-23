from o3dModel import Model
import numpy as np
import tokenize

fmflag=False

class O3dConvX(Model):
    @staticmethod
    def transform(obj:Model):
        if isinstance(obj,Model):
            obj.__class__=O3dConvX
    def exportDirectXAsciiFrame(self,filename):
        with open(filename,'w')as file:
            file.write("xof 0302txt 0064\ntemplate Header {\n <3D82AB43-62DA-11cf-AB39-0020AF71E433>\n WORD major;\n WORD minor;\n DWORD flags;\n}\n\ntemplate Vector {\n <3D82AB5E-62DA-11cf-AB39-0020AF71E433>\n FLOAT x;\n FLOAT y;\n FLOAT z;\n}\n\ntemplate Coords2d {\n <F6F23F44-7686-11cf-8F52-0040333594A3>\n FLOAT u;\n FLOAT v;\n}\n\ntemplate Matrix4x4 {\n <F6F23F45-7686-11cf-8F52-0040333594A3>\n array FLOAT matrix[16];\n}\n\ntemplate ColorRGBA {\n <35FF44E0-6C7C-11cf-8F52-0040333594A3>\n FLOAT red;\n FLOAT green;\n FLOAT blue;\n FLOAT alpha;\n}\n\ntemplate ColorRGB {\n <D3E16E81-7835-11cf-8F52-0040333594A3>\n FLOAT red;\n FLOAT green;\n FLOAT blue;\n}\n\ntemplate Material {\n <3D82AB4D-62DA-11cf-AB39-0020AF71E433>\n ColorRGBA faceColor;\n FLOAT power;\n ColorRGB specularColor;\n ColorRGB emissiveColor;\n [...]\n}\n\ntemplate MeshFace {\n <3D82AB5F-62DA-11cf-AB39-0020AF71E433>\n DWORD nFaceVertexIndices;\n array DWORD faceVertexIndices[nFaceVertexIndices];\n}\n\ntemplate MeshTextureCoords {\n <F6F23F40-7686-11cf-8F52-0040333594A3>\n DWORD nTextureCoords;\n array Coords2d textureCoords[nTextureCoords];\n}\n\ntemplate MeshMaterialList {\n <F6F23F42-7686-11cf-8F52-0040333594A3>\n DWORD nMaterials;\n DWORD nFaceIndexes;\n array DWORD faceIndexes[nFaceIndexes];\n [Material]\n}\n\ntemplate MeshNormals {\n <F6F23F43-7686-11cf-8F52-0040333594A3>\n DWORD nNormals;\n array Vector normals[nNormals];\n DWORD nFaceNormals;\n array MeshFace faceNormals[nFaceNormals];\n}\n\ntemplate Mesh {\n <3D82AB44-62DA-11cf-AB39-0020AF71E433>\n DWORD nVertices;\n array Vector vertices[nVertices];\n DWORD nFaces;\n array MeshFace faces[nFaces];\n [...]\n}\n\ntemplate FrameTransformMatrix {\n <F6F23F41-7686-11cf-8F52-0040333594A3>\n Matrix4x4 frameMatrix;\n}\n\ntemplate Frame {\n <3D82AB46-62DA-11cf-AB39-0020AF71E433>\n [...]\n}\n\n")
            for i in range(self.materials.amount):
                fd=self.materials.fdata[i]
                file.write(f"Material Material_{i+1} {{\n"\
					f" {fd[0]:.6f};{fd[1]:.6f};{fd[2]:.6f};{fd[3]:.6f};;\n"\
					f" {fd[10]:.6f};\n"\
					f" {fd[4]:.6f};{fd[5]:.6f};{fd[6]:.6f};;\n"\
					f" {fd[7]:.6f};{fd[8]:.6f};{fd[9]:.6f};;\n"\
					f" TextureFilename {{\n"\
					f" \"{self.materials.names[i]}\";\n"\
					f" }}\n"\
					f"}}\n"\
					f"\n")    
            #file.write()
            file.write("Header {\n 1;\n 0;\n 1;\n}\n")
            file.write("\nFrame Model1 {\n FrameTransformMatrix {\n")
            for o in range(len(self.matrix)):
                i=self.matrix[o]
                file.write(f"  {i[0]:.6f},{i[1]:.6f},{i[2]:.6f},{i[3]:.6f}")
                if o!=3:
                    file.write(",\n")
                else:
                    file.write(";;\n")
            file.write(" }\nMesh Model1 {\n")
            file.write(f" {self.vertices.amount};\n")
            for i in range(self.vertices.amount):
                o=self.vertices.coords[i]
                file.write(f" {o[0]:.6f};{o[2]:.6f};{o[1]:.6f};")
                if i!=self.vertices.amount-1:
                    file.write(",\n")
                else:
                    file.write(";\n")
            file.write(f"\n {self.faces.amount};\n")
            for i in range(self.faces.amount):
                o=self.faces.indices[i]
                file.write(f" 3;{o[2]},{o[1]},{o[0]};")
                if i!=self.faces.amount-1:
                    file.write(",\n")
                else:
                    file.write(";\n")
            file.write("\n MeshMaterialList {\n")
            file.write(f"  {self.materials.amount};\n")
            file.write(f"  {self.faces.amount};\n")
            for i in range(self.faces.amount):
                o=self.faces.materialIndice[i]
                file.write(f"  {o[0]}")
                if i!=self.faces.amount-1:
                    file.write(",\n")
                else:
                    file.write(";;\n")
            for i in range(self.materials.amount):
                file.write(f"  {{Material_{i+1}}}\n")
            file.write(" }\n\n MeshNormals {\n")
            file.write(f"  {self.vertices.amount};\n")
            for i in range(self.vertices.amount):
                o=self.vertices.normals[i]
                file.write(f"  {o[0]:.6f};{o[2]:.6f};{o[1]:.6f};")
                if i!=self.vertices.amount-1:
                    file.write(",\n")
                else:
                    file.write(";\n")
            file.write(f"\n  {self.faces.amount};\n")
            for i in range(self.faces.amount):
                o=self.faces.indices[i]
                file.write(f"  3;{o[1]},{o[0]},{o[2]};")
                if i!=self.faces.amount-1:
                    file.write(",\n")
                else:
                    file.write(";\n")
            file.write(" }\n\n MeshTextureCoords {\n")
            file.write(f"  {self.vertices.amount};\n")
            for i in range(self.vertices.amount):
                o=self.vertices.texcoords[i]
                file.write(f"  {o[0]:.6f};{(1.-o[1]):.6f};")
                if i!=self.vertices.amount-1:
                    file.write(",\n")
                else:
                    file.write(";\n")
            file.write("  }\n }\n}")

    def importDirectXAsciiFrame(self,filename)->bool:
        with open(filename,'rb') as file:
            tokens=tokenize.tokenize(file.readline)
            token=tokens.__next__()
            if not(token.type==59 and token.string=='utf-8'):
                print('expected utf-8 but '+token.string+' present')
                return False
            token=tokens.__next__()
            if not(token.type==1 and token.string=='xof'):
                print('expected xof but '+token.string+' present')
                return False
            while True:
                token=tokens.__next__()
                if token.type==4 or token.type==58:
                    break
            def nt():
                token=tokens.__next__()
                while token.exact_type==4 or token.exact_type==58:
                    token=tokens.__next__()
                return token
            symbols={
                ';':13,'{':25,'}':26,',':12,'-':15
            }

            strucs={}#stub for vf
            def ss(symbol:str):
                token=nt()
                if token.exact_type!=symbols[symbol]:
                    print(f'expected {symbol} but '+token.string+' present')
                    return False
                return True
            def vn(varname:str):
                token=tokens.__next__()
                if token.exact_type==25:
                    return '{'
                if token.type!=1:
                    print(f'expected {varname} but '+token.string+' present of type '+str(token.type)+" "+str(token.exact_type))
                    return False
                return token.string
            def et(tokenName:str):
                token=nt()
                if not(token.exact_type==1 and token.string==tokenName):
                    print(f'expected {tokenName} but '+token.string+' present of type '+str(token.type)+" "+str(token.exact_type))
                    return False
                return True
            def st():#string
                token=nt()
                if token.exact_type!=3:
                    print('expected <string> but '+token.string+' present of type '+str(token.type)+" "+str(token.exact_type))
                    return False
                return token.string[1:-1]
            def rv(count:int):
                vec=[]
                for _ in range(count):
                    token=nt()
                    if token.exact_type==15:
                        fv=-1
                        token=tokens.__next__()
                    else:
                        fv=1
                    if token.exact_type!=2:
                        print('expected number but '+token.string+' present')
                        return False
                    vec.append(fv*float(token.string))
                    if not ss(';'):return False
                return vec
            def fv(count:int):
                vec=[]
                for i in range(count):
                    token=nt()
                    if token.exact_type==15:
                        fv=-1
                        token=tokens.__next__()
                    else:
                        fv=1
                    if token.exact_type!=2:
                        print('expected number but '+token.string+' present')
                        return False
                    vec.append(fv*float(token.string))
                    if i!=count-1:
                        if not ss(','):return False
                return vec
            def vf()->bool:
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

            def mf()->bool:
                v=vn('<materialName>')
                if not v:return False 
                if v!='{':
                    if not ss('{'):return False
                faceColor=rv(4)
                if not faceColor:return False
                if not ss(';'):return False
                power=rv(1)
                if not power:return False
                specularColor=rv(3)
                if not specularColor:return False
                if not ss(';'):return False
                emissiveColor=rv(3)
                if not emissiveColor:return False
                if not ss(';'):return False
                if not et('TextureFilename'):return False
                if not ss('{'):return False
                materialName=st()
                if not materialName:return False
                if not ss(';'):return False
                if not ss('}'):return False
                if not ss('}'):return False
                fdata=[]
                fdata.extend(faceColor)
                fdata.extend(specularColor)
                fdata.extend(emissiveColor)
                fdata.extend(power)
                self.materials.fdata.append(fdata)
                self.materials.names.append(materialName)
                if not fmflag:
                    self.materials.amount+=1
                return True
            def tf()->bool:
                v=vn('<structName>')
                if not v:return False 
                if v!='{':
                    if not ss('{'):return False
                counter=0
                while counter>=0:
                    token=tokens.__next__()
                    if token.exact_type==25:#{
                        counter+=1
                        continue
                    if token.exact_type==26:#}
                        if counter==0:
                            return True
                        else:
                            counter-=1
                print('no opening bracet }')
                return False
            def hf()->bool:
                if not ss('{'):return False
                if not rv(3):return False
                if not ss('}'):return False
                return True
            def ff()->bool:
                v=vn('<modelName>')
                if not v:return False
                if v!='{':
                    if not ss('{'):return False
                if not vf():return False
                return True
            def ft()->bool:
                if not ss('{'):return False
                matrix=fv(16)
                if not matrix:return False
                if self.matrix==[]:
                    self.matrix=np.array(matrix,dtype=np.dtype('<f4')).reshape(4,4)
                if not ss(';'):return False
                if not ss(';'):return False
                if not ss('}'):return False
                return True
            def me()->bool:
                v=vn('<modelName>')
                if not v:return False
                if v!='{':
                    if not ss('{'):return False
                pcount=rv(1)
                if not pcount:return False
                pcount=int(pcount[0])
                if self.vertices.amount==0:
                    self.vertices.amount=pcount
                if pcount!=self.vertices.amount:
                    print('Points amount mismatch')
                    return False
                matrix=[]
                for i in range(pcount):
                    line=rv(3)
                    if not line:return False
                    matrix.append(line)
                    if i!=pcount-1:
                        if not ss(','):return False
                    else:
                        if not ss(';'):return False
                if self.vertices.coords==[]:
                    self.vertices.coords=np.array(matrix,dtype=np.dtype('<f4')).reshape(pcount,3)
                
                fcount=rv(1)
                if not fcount:return False
                fcount=int(fcount[0])
                if self.faces.amount==0:
                    self.faces.amount=fcount
                if fcount!=self.faces.amount:
                    print('Faces amount mismatch')
                    return False
                matrix=[]
                for i in range(fcount):
                    polyVert=rv(1)
                    if not polyVert or polyVert[0]!=3:
                        print("The only supported type of polygons is triangles")
                        return False
                    line=fv(3)
                    if not line:return False
                    matrix.append(line)
                    if not ss(';'):return False
                    if i!=fcount-1:
                        if not ss(','):return False
                    else:
                        if not ss(';'):return False
                if self.faces.indices==[]:
                    self.faces.indices=np.array(matrix,dtype=np.dtype('<u4')).reshape(fcount,3)
                if not vf():return False
                return True
            def mm()->bool:
                global fmflag
                if not ss('{'):return False
                mcount=rv(1)
                if not mcount:return False
                mcount=int(mcount[0])
                if self.materials.amount==0:
                    fmflag=True
                    self.materials.amount=mcount
                if mcount!=self.materials.amount:
                    print('Material amount mismatch')
                    return False
                fcount=rv(1)
                if not fcount:return False
                fcount=int(fcount[0])
                if self.faces.amount==0:
                    self.faces.amount=fcount
                if fcount!=self.faces.amount:
                    print('Faces amount mismatch')
                    return False
                matrix=[]
                if fmflag:
                    for i in range(fcount):
                        line=rv(1)
                        if not line:return False
                        matrix.append(line)
                        if i!=fcount-1:
                            if not ss(','):return False
                        else:
                            if not ss(';'):return False
                else:
                    matrix=fv(fcount)
                    if not matrix: return False
                    if not ss(';'):return False
                    if not ss(';'):return False

                if self.faces.materialIndice==[]:
                    self.faces.materialIndice=np.array(matrix,dtype=np.dtype('<u4')).reshape(fcount,1)
                
                if fmflag:
                    if not vf(): return False
                    return True
                for _ in range(mcount):
                    if not ss('{'):return False
                    v=vn('<materialName>')
                    if not v:return False
                    if v=='{':
                        print('Nope, not this time')
                        return False
                    if not ss('}'):return False
                if not ss('}'):return False
                return True
            def mn()->bool:
                if not ss('{'):return False
                pcount=rv(1)
                if not pcount:return False
                pcount=int(pcount[0])
                if self.vertices.amount==0:
                    self.vertices.amount=pcount
                if pcount!=self.vertices.amount:
                    print('Points amount mismatch')
                    return False
                matrix=[]
                for i in range(pcount):
                    line=rv(3)
                    if not line:return False
                    matrix.append(line)
                    if i!=pcount-1:
                        if not ss(','):return False
                    else:
                        if not ss(';'):return False
                if self.vertices.normals==[]:
                    self.vertices.normals=np.array(matrix,dtype=np.dtype('<f4')).reshape(pcount,3)
                fcount=rv(1)
                if not fcount:return False
                fcount=int(fcount[0])
                if self.faces.amount==0:
                    self.faces.amount=fcount
                if fcount!=self.faces.amount:
                    print('Faces amount mismatch')
                    return False
                matrix=[]
                for i in range(fcount):
                    polyVert=rv(1)
                    if not polyVert or polyVert[0]!=3:
                        print("The only supported type of polygons is triangles")
                        return False
                    line=fv(3)
                    if not line:return False
                    matrix.append(line)
                    if not ss(';'):return False
                    if i!=fcount-1:
                        if not ss(','):return False
                    else:
                        if not ss(';'):return False
                if self.faces.indices==[]:
                    self.faces.indices=np.array(matrix,dtype=np.dtype('<u4')).reshape(fcount,3)
                if not ss('}'):return False
                return True
            def mt()->bool:
                global fmflag
                if not ss('{'):return False
                pcount=rv(1)
                if not pcount:return False
                pcount=int(pcount[0])
                if self.vertices.amount==0:
                    self.vertices.amount=pcount
                if pcount!=self.vertices.amount:
                    print('Points amount mismatch')
                    return False
                matrix=[]
                for i in range(pcount):
                    line=rv(2)
                    if not line:return False
                    matrix.append(line)
                    if fmflag:
                        if i==pcount-1:
                            if not ss(','):return False
                        else:
                            if not ss(';'):return False
                    else:
                        if i!=pcount-1:
                            if not ss(','):return False
                        else:
                            if not ss(';'):return False
                if self.vertices.texcoords==[]:
                    self.vertices.texcoords=np.array(matrix,dtype=np.dtype('<f4')).reshape(pcount,2)
                if not ss('}'):return False
                return True
            strucs={
                'Material':mf,
                'template':tf,
                'Header':hf,
                'Frame':ff,
                'FrameTransformMatrix':ft,
                'Mesh':me,
                'MeshMaterialList':mm,
                'MeshNormals':mn,
                'MeshTextureCoords':mt,
            }
            for i in tokens:
                if i.type==1:
                    if i.string in strucs:
                        if not strucs[i.string]():
                            print("failed parsing "+i.string)
                            return False
                    else:
                        print(i.type,i.exact_type,"'"+i.string+"'")    
                elif i.type==4 or i.type==58:
                    pass
                else:
                    print(i.type,i.exact_type,"'"+i.string+"'")
            if self.vertices.normals==[]:
                self.vertices.normals=np.c_[np.ones([self.vertices.amount,1]),np.zeros([self.vertices.amount,2])].astype(np.dtype('<f4'))
            self.materials.fdata=np.array(self.materials.fdata,dtype=np.dtype('<f4')).reshape(self.materials.amount,11).copy()
            self.vertices.coords=np.c_[self.vertices.coords[:,0],self.vertices.coords[:,2],self.vertices.coords[:,1]].copy()
            self.vertices.normals=np.c_[self.vertices.normals[:,0],self.vertices.normals[:,2],self.vertices.normals[:,1]].copy()
            self.vertices.texcoords[:,1]=1.-self.vertices.texcoords[:,1]
            self.faces.indices=np.c_[self.faces.indices[:,1],self.faces.indices[:,0],self.faces.indices[:,2]].copy()
            self.vertices.__store=np.c_[self.vertices.coords,self.vertices.normals,self.vertices.texcoords]
            self.faces.__store=np.c_[self.faces.indices,self.faces.materialIndice]
            if self.matrix==[]:
                self.matrix=np.array([[1.,0.,0.,0.],[0.,1.,0.,0.],[0.,0.,1.,0.],[0.,0.,0.,1.]],dtype=np.dtype('<f4'))
            if True:pass                
            else:
                print("Unsupported directx ascii frame format")
        return True