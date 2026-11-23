import numpy as np
def load_cube(path):
    size=None; data=[]
    for line in open(path):
        s=line.strip()
        if not s or s.startswith('#'): continue
        if s.startswith('LUT_3D_SIZE'): size=int(s.split()[1]); continue
        if s[0].isalpha(): continue
        data.append([float(x) for x in s.split()])
    a=np.array(data,dtype=np.float32)
    return a.reshape(size,size,size,3)  # [b][g][r] since r fastest
def apply_lut(img, lut, strength=1.0):
    """img float32 HxWx3 in 0..1 -> graded; trilinear."""
    n=lut.shape[0]-1
    x=np.clip(img,0,1)*n
    i0=np.floor(x).astype(np.int32); i0=np.minimum(i0,n-1); f=x-i0
    r0,g0,b0=i0[...,0],i0[...,1],i0[...,2]; fr,fg,fb=f[...,0:1],f[...,1:2],f[...,2:3]
    def L(b,g,r): return lut[b,g,r]
    c000=L(b0,g0,r0); c100=L(b0,g0,r0+1); c010=L(b0,g0+1,r0); c110=L(b0,g0+1,r0+1)
    c001=L(b0+1,g0,r0); c101=L(b0+1,g0,r0+1); c011=L(b0+1,g0+1,r0); c111=L(b0+1,g0+1,r0+1)
    c00=c000*(1-fr)+c100*fr; c10=c010*(1-fr)+c110*fr; c01=c001*(1-fr)+c101*fr; c11=c011*(1-fr)+c111*fr
    c0=c00*(1-fg)+c10*fg; c1=c01*(1-fg)+c11*fg
    out=c0*(1-fb)+c1*fb
    return img*(1-strength)+out*strength if strength<1 else out
def pre_adjust(img, exposure=0.0, contrast=0.0, gamma=1.0):
    """exposure in stops, contrast -1..1 S-curve around 0.5 (in gamma space)."""
    x=img*(2.0**exposure)
    if gamma!=1.0: x=np.clip(x,0,1)**(1/gamma)
    if contrast:
        x=np.clip(x,0,1); k=1+contrast
        x=0.5+(x-0.5)*k
    return np.clip(x,0,1)
