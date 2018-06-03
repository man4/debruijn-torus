from torus import Torus

values = [
    [0,0,1,1,0,0,1,0,0,0,1,1,0,1,1,1],
    [0,0,1,1,0,0,0,1,0,1,1,0,0,0,0,1],
    [0,0,1,1,0,1,1,1,0,0,1,1,0,0,1,0],
    [1,1,0,0,1,0,1,1,1,0,0,1,1,0,1,1],
]
m, n = 3, 2
torus = Torus(values, m, n, 'storage.txt')
torus.transpose()
torus.make(seed=[0,0,0,1,1,1,0,1])
torus.make(seed=[0,0,0,1,1,1,0,1])
torus.transpose()
torus.make()
torus.save('output-shiu.png')
