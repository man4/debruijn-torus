from torus import Torus

values = [
    [0,0,1,0],
    [0,0,0,1],
    [0,1,1,1],
    [1,0,1,1],
]
m, n = 2, 2
torus = Torus(values, m, n, 'storage.txt')
torus.make()
torus.save('output-3x2.png', square_size=24)
