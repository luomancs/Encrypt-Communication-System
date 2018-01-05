import cPickle
import struct

data = [3, 4, 5]
cPickle.dump(data, open("test.txt", "w"))
cPickle.load(open("test.txt", "r"))

size = struct.pack("L", len(data))
print repr(size)
