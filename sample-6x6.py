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
torus.make()
torus.transpose()
torus.make()
torus.make()
torus.transpose()
torus.make()
torus.make()
torus.transpose()
torus.make()
torus.save('output-6x6.png', tile_width=32, tile_height=32)
