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
torus.make()
torus.save('output-3x3.png', square_size=12)
torus.make()
torus.transpose()
torus.make()
torus.save('output-4x4.png', square_size=2)
torus.make()
torus.transpose()
torus.make()
torus.save('output-5x5.png')
