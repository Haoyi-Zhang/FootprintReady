"""Vector drawing primitives; copied into each independent project generator."""
import argparse
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, Circle, FancyArrowPatch

plt.rcParams.update({'font.family':'STIXGeneral', 'mathtext.fontset':'stix',
                     'font.size':9, 'pdf.fonttype':42, 'ps.fonttype':42,
                     'text.usetex':False, 'axes.unicode_minus':False})
CM = 1 / 2.54

class Drawing:
    def __init__(self, bounds):
        x0,y0,x1,y1 = bounds
        self.fig = plt.figure(figsize=((x1-x0)*CM,(y1-y0)*CM))
        self.ax = self.fig.add_axes([0,0,1,1], xlim=(x0,x1), ylim=(y0,y1))
        self.ax.set_aspect('equal'); self.ax.axis('off')
        self.nodes = {}
        self.labels = []

    def text(self,x,y,label,size=9,ha='center',va='center'):
        artist=self.ax.text(x,y,label,fontsize=size,ha=ha,va=va,
                            linespacing=1.15,clip_on=False,zorder=4)
        self.labels.append([artist,None])
        return artist

    def box(self,name,x,y,w,h,label,dashed=False,shape='rect',size=9):
        style = {'edgecolor':'black','facecolor':'white','linewidth':.55,
                 'linestyle':(0,(4,3)) if dashed else 'solid', 'zorder':2}
        if shape == 'diamond':
            obj = Polygon([(x-w/2,y),(x,y+h/2),(x+w/2,y),(x,y-h/2)],**style)
        elif shape == 'circle': obj = Circle((x,y),w/2,**style)
        else: obj = Rectangle((x-w/2,y-h/2),w,h,**style)
        self.ax.add_patch(obj); self.text(x,y,label,size)
        self.labels[-1][1]=(x-w/2,y-h/2,x+w/2,y+h/2)
        self.nodes[name] = (x,y,w,h,shape)

    def point(self,name,side):
        x,y,w,h,_ = self.nodes[name]
        return {'n':(x,y+h/2),'s':(x,y-h/2),'e':(x+w/2,y),
                'w':(x-w/2,y),'nw':(x-w/2,y+h/2),
                'ne':(x+w/2,y+h/2),'c':(x,y)}[side]

    def line(self,points,dashed=False):
        xs,ys=zip(*points)
        self.ax.plot(xs,ys,color='black',linewidth=.55,
                     linestyle=(0,(4,3)) if dashed else 'solid',zorder=1)

    def arrow(self,p,q,dashed=False,via=()):
        points=[p,*via,q]
        if via:self.line(points[:-1],dashed)
        self.ax.add_patch(FancyArrowPatch(points[-2],points[-1],
                         arrowstyle='-|>',mutation_scale=7.5,linewidth=.55,
                         color='black',shrinkA=0,shrinkB=0,
                         linestyle=(0,(4,3)) if dashed else 'solid',zorder=1))

    def edge(self,a,b,sa='s',sb='n',**kwargs):
        self.arrow(self.point(a,sa),self.point(b,sb),**kwargs)

    def frame(self,x,y,w,h):
        self.ax.add_patch(Rectangle((x,y),w,h,fill=False,edgecolor='black',
                                   linewidth=.55,linestyle=(0,(4,3)),zorder=0))

    def save(self,out,name):
        # Fixed physical canvas: do not enlarge or rasterize the scientific figure.
        self.fig.canvas.draw()
        renderer=self.fig.canvas.get_renderer()
        x0,x1=self.ax.get_xlim();y0,y1=self.ax.get_ylim()
        for artist,node in self.labels:
            b=artist.get_window_extent(renderer).transformed(self.ax.transData.inverted())
            if b.x0<x0-.02 or b.x1>x1+.02 or b.y0<y0-.02 or b.y1>y1+.02:
                raise ValueError(name+': clipped label '+repr(artist.get_text()))
            if node and (b.x0<node[0]-.02 or b.x1>node[2]+.02 or b.y0<node[1]-.02 or b.y1>node[3]+.02):
                raise ValueError(name+': label exceeds node '+repr(artist.get_text()))
        self.fig.savefig(out/(name+'.pdf'),format='pdf',
                         metadata={'Creator':'Python Matplotlib','Producer':None,
                                   'CreationDate':None,'ModDate':None})
        plt.close(self.fig)





def boundary(out):
    d=Drawing((-.2,-2.8,16.4,1.45))
    for name,x,label in [
        ('a',1.3,'$m=0,\\ R=\\{a\\}$\n$D=\\{a\\}$'),
        ('b',5.5,'$m=0,\\ R=\\{a\\}$\n$D=\\varnothing$'),
        ('c',9.7,'$m=1,\\ R=\\varnothing$\n$D=\\varnothing$'),
        ('e',13.9,'$m=1,\\ R=\\{a\\}$\n$D=\\varnothing$')]:
        d.box(name,x,0,2.9,.9,label)
    d.box('r',7.6,-2,2.9,.9,'$m=1,\\ R=\\{a\\}$\n$D=\\{a\\}$')
    for a,b,x,label in [('a','b',3.4,'store $a$\n$+8$'),
                         ('b','c',7.6,'destroying switch\n$+9$'),
                         ('c','e',11.8,'load $a$\n$+6$')]:
        d.edge(a,b,'e','w');d.text(x,.9,label,size=8.5)
    d.arrow(d.point('a','s'),d.point('r','w'),True,via=((1.3,-2),))
    d.text(3.8,-2.4,'retaining switch: $+9$',size=8.5)
    d.text(10,-1.8,'Solid: destructive architecture\nDashed: retaining architecture',ha='left',size=8.5)
    d.save(out,'boundary')

def schedule(out):
    d=Drawing((-.65,-2.05,6.1,2))
    for name,x,y,label in [('0',1.2,1.1,'$0$'),('2',2.65,1.1,'$2$'),
                            ('1',1.2,-.15,'$1$'),('3',2.65,-.15,'$3$'),
                            ('4',4.2,.48,'$4$')]:
        d.box(name,x,y,.62,.62,label,shape='circle')
    for a,b in [('0','2'),('1','3'),('2','4'),('3','4')]:d.edge(a,b,'e','w')
    for x,y,label,n in [(0,1.1,'$x$','0'),(0,-.15,'$w$','1')]:
        d.text(x,y,label);d.arrow((x+.16,y),d.point(n,'w'))
    d.arrow(d.point('4','e'),(5.2,.48));d.text(5.45,.48,'$y$')
    for x,y,label in [(1.2,1.7,'$m_0$'),(2.65,1.7,'$m_0$'),
                      (1.2,-.75,'$m_1$'),(2.65,-.75,'$m_1$'),(4.2,1.1,'$m_0/m_1$')]:
        d.text(x,y,label)
    d.text(0,-1.25,'list: $0\\,\\to\\,1\\,\\to\\,2\\,\\to\\,3\\,\\to\\,4$',ha='left')
    d.text(0,-1.8,'ready: $0\\,\\to\\,2\\,\\to\\,1\\,\\to\\,3\\,\\to\\,4$',ha='left')
    d.save(out,'schedule')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,default=Path(__file__).resolve().parents[1]/'figures')
    args=parser.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    boundary(args.out);schedule(args.out)
