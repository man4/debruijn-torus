import itertools
import operator
import os
import shutil
import time
from PIL import Image

class Torus():
    """Class that represents a binary de Bruijn torus."""

    def __init__(self, values, m, n, storage):
        """Initializes an (r, s; m, n) binary de Bruijn torus.

        An (r, s; m, n) binary de Bruijn torus is an r-by-s binary matrix that
        contains every m-by-n binary matrix exactly once. Each edge of the
        matrix wraps around to the opposite side.

        The torus dimensions should satisfy r * s = 2^(m * n).

        values: A two-dimensional list with dimensions r-by-s, containing the
            elements of the torus. Each element must be either 0 or 1.
        m, n: Integers representing the dimensions of the sub-matrices.
        storage: Name of a file that will be used as storage. If the name
            already exists, the file will be overwritten.

        For example, the following code initializes a (4, 4; 2, 2) torus:
            values = [
                [0,0,1,0],
                [0,0,0,1],
                [0,1,1,1],
                [1,0,1,1],
            ]
            torus = Torus(values, 2, 2, 'storage.txt')
        """
        self.r = len(values)
        self.s = len(values[0])
        self.m = m
        self.n = n
        if self.r * self.s != 2 ** (self.m * self.n):
            raise ValueError('Dimension mismatch')

        self.row_sums = 0
        self.col_sums = 0
        for row in values:
            row_num = self._list_to_num(row)
            self.row_sums <<= 1
            self.row_sums += self._popcount(row_num) % 2
            self.col_sums ^= row_num

        self.file = storage
        self.temp = self.file + '.tmp'
        with open(self.file, 'w+b') as f:
            self._write_from_array(f, self._bytes(self.s), values)

    # int -> file
    def _write_from_num(self, f, length, lines):
        for num in lines:
            f.write(num.to_bytes(length, 'big'))

    # file -> int
    def _read_to_num(self, f):
        return int.from_bytes(f.read(self._bytes(self.s)), 'big')

    # list/bytearray -> file
    def _write_from_array(self, f, length, lines):
        for line in lines:
            num = int(''.join(map(str, line)), 2)
            f.write(num.to_bytes(length, 'big'))

    # file -> bytearray
    def _read_to_array(self, f):
        num = int.from_bytes(f.read(self._bytes(self.s)), 'big')
        line = f'{num:0{self.s}b}'
        return bytearray(map(int, line))

    # return number of 1's in binary representation of num
    def _popcount(self, num):
        return f'{num:b}'.count('1')

    # list -> int
    def _list_to_num(self, line):
        return int(''.join(map(str, line)), 2)

    # return number of bytes required to hold n bits
    def _bytes(self, n):
        return (n + 7) // 8

    @staticmethod
    def debruijn(order):
        """Returns a binary de Bruijn sequence of the given order as a list.

        Implements the algorithm from [1], which runs in amortized O(1) time
        per bit and O(n) space. Used as the default seed for make().

        [1] J.-P. Duval. "Génération d'une section des classes de conjugaison
            et arbre des mots de Lyndon de longueur bornée," Theoretical
            Computer Science, Vol. 60, Issue 3 (1988), pp. 255-283.
        """
        seq = []
        word = [0] * order
        i = 1
        while i:
            if order % i == 0:
                seq.extend(word[:i])
            for j in range(order - i):
                word[i+j] = word[j]
            i = order
            while i and word[i-1]:
                i -= 1
            if i:
                word[i-1] = 1
        return seq

    def get_size(self):
        """Returns the dimensions of the torus as a tuple (r, s, m, n)."""
        return self.r, self.s, self.m, self.n

    def transpose(self):
        """Swaps the dimensions of the torus.

        This method is quite memory- and time-intensive, because the whole
        torus is read into memory. When operating on very large tori, the
        transpose operation is likely to be the bottleneck.
        """
        start_time = time.perf_counter()

        shutil.copyfile(self.file, self.temp)
        with open(self.file, 'w+b') as f, open(self.temp, 'rb') as old:
            lines = [self._read_to_array(old) for _ in range(self.r)]
            self._write_from_array(f, self._bytes(self.r), zip(*lines))
        total_time = time.perf_counter() - start_time
        print(f'Transposed {self.r}x{self.s} torus in {total_time:.3f}s')
        os.remove(self.temp)

        self.r, self.s = self.s, self.r
        self.m, self.n = self.n, self.m
        self.row_sums, self.col_sums = self.col_sums, self.row_sums

    def make(self, seed=None):
        """Constructs a larger torus from the current torus.

        This method implements the constructions of [2]. Suppose the current
        torus has dimensions (r, s; m, n).

        When the sum of each column is even, Construction 5.1 from [2] is
        applicable and yields a torus of size (r, s * 2^n; m + 1, n).

        When the sum of each column is odd, Construction 5.5 from [2] is
        applicable and yields a torus of size (2 * r, s * 2^(n-1); m + 1, n).

        In all other cases, this method will return a ValueError.

        seed: A list containing a binary de Bruijn sequence.
            For even column sums, seed is an order-n de Bruijn sequence that
                starts with n zeroes.
            For odd column sums, seed is an order-(n-1) de Bruijn sequence that
                starts with n-1 zeroes.
            If seed is None, a default seed will be generated from debruijn().

        Notes:
            For n >= 2, the result of Construction 5.1 is guaranteed to have
                even row sums. Hence, the transpose of this result may be used
                again in Construction 5.1.
            There are also parity guarantees for some other tori. See [2] for
                more details.

        [2] C.T. Fan, S.M. Fan, S.L. Ma, and M.K. Siu. "On de Bruijn arrays,"
            Ars Combinatoria, Vol. 19A (1985), pp. 205-213.
        """
        start_time = time.perf_counter()

        # Determine which construction to use
        EVEN, ODD = 0, 1
        if self.col_sums == 0:
            MODE = EVEN
            print('Using even construction')
        elif self.col_sums == (1 << self.s) - 1:
            MODE = ODD
            print('Using odd construction')
        else:
            raise ValueError('Column sums must be all even or all odd')

        # Construct first line
        next_line = [0] * self.s

        if MODE == EVEN:
            if seed is None:
                seed = Torus.debruijn(self.n)
            next_line += seed[1:] * self.s
        else:
            if self.n == 2:
                next_line += [0, 1] * (self.s // 2)
            elif self.n >= 3:
                if seed is None:
                    seed = Torus.debruijn(self.n - 1)
                seed_cumsum = list(itertools.accumulate(
                    seed[:-1], operator.xor))
                next_line += seed_cumsum * self.s

        next_line = self._list_to_num(next_line)
        result = [next_line]

        # Keep track of row and column sums
        self.row_sums = self._popcount(next_line) % 2
        self.col_sums = next_line

        if MODE == EVEN:
            num_rows = self.r
            num_copies = 2 ** self.n
        else:
            num_rows = 2 * self.r
            num_copies = 2 ** (self.n - 1)

        shutil.copyfile(self.file, self.temp)
        with open(self.file, 'w+b') as f, open(self.temp, 'rb') as old:
            for row in range(num_rows - 1):
                if row == self.r: # only occurs when MODE == ODD
                    old.seek(0)
                old_line = self._read_to_num(old)

                # Repeat bit pattern num_copies times
                old_line_repeated = 0
                for i in range(num_copies):
                    old_line_repeated += old_line << (self.s * i)
                next_line ^= old_line_repeated

                result.append(next_line)
                self.row_sums <<= 1
                self.row_sums += self._popcount(next_line) % 2
                self.col_sums ^= next_line

                # Periodically write result to file
                if len(result) % min(num_rows, 2 ** 10) == 0:
                    self._write_from_num(
                        f, self._bytes(self.s * num_copies), result)
                    result.clear()
                    total_time = time.perf_counter() - start_time
                    print(f'row {row+2}/{num_rows} time {total_time:.3f}s')
        os.remove(self.temp)

        self.r = num_rows
        self.s *= num_copies
        self.m += 1

    def save(self, name, tile_width=1, tile_height=1, square_size=1):
        """Saves the torus as a monochromatic image.

        Converts each element in the torus to a 1-bit pixel:
            0 -> black
            1 -> white
        The resulting image is saved to the given name, which should contain
        an extension corresponding to a lossless image format, such as .png.

        The values of the torus are packed into raw bytes, with 8 single-bit
        values per byte. Because of this compact representation, the function
        does not work if the resulting image width is fewer than 8 pixels.

        To keep image sizes manageable, there is an option to cut up the
        resulting image into a grid of smaller images. In this case, the files
        will be named with their location in the grid.

        For example, save('output.png', tile_width=4, tile_height=4) creates
        a 4-by-4 grid of images. The image in the first row and third column
        of the grid will be named 'output_1_3.png'.

        To visualize small tori more easily, there is an option to convert
        each value of the torus into a square block of pixels, effectively
        upscaling the output image.

        name: Name of the output image file.
        tile_width, tile_height: Dimensions for cutting up the output image.
        square_size: Factor used to upscale the output image.
        """
        if self.s % tile_width or self.r % tile_height:
            raise ValueError('Tile dimensions must divide torus dimensions')

        img_width = self.s // tile_width
        img_height = self.r // tile_height
        img_dim = (img_width * square_size, img_height * square_size)
        if img_width % 8:
            raise ValueError('Output image width must be at least 8')

        # Get bytes corresponding to a row of square blocks of pixels
        def get_next_data():
            start = i * self._bytes(self.s) + w * self._bytes(img_width)
            end = start + self._bytes(img_width)
            next_data = data[start:end]

            # Repeat each bit square_size times
            if square_size > 1:
                next_data = int.from_bytes(next_data, 'big')
                next_data = f'{next_data:0{img_width}b}'
                next_data = ''.join(i * square_size for i in next_data)
                next_data = (int(next_data, 2)
                    .to_bytes(square_size * self._bytes(img_width), 'big'))
                next_data *= square_size
            return next_data

        with open(self.file, 'rb') as f:
            if tile_width == tile_height == square_size == 1:
                data = f.read()
                img = Image.frombytes('1', img_dim, data, 'raw', '1')
                img.save(name)
                return

            base, ext = os.path.splitext(name)

            for h in range(tile_height):
                data = f.read(img_height * self._bytes(self.s))

                for w in range(tile_width):
                    curr_data = bytearray()
                    for i in range(img_height):
                        curr_data.extend(get_next_data())
                    curr_data = bytes(curr_data)

                    img = Image.frombytes('1', img_dim, curr_data, 'raw', '1')
                    if tile_width == tile_height == 1:
                        img.save(name)
                    else:
                        img.save(f'{base}_{h+1}_{w+1}{ext}')
