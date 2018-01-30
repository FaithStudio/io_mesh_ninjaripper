from typing import List, Tuple

try:
    from .ByteIO import ByteIO
except:
    from ByteIO import ByteIO


class RIPAttrTypes:
    POSITION = "POSITION"
    NORMAL = "NORMAL"
    TEXCOORD = "TEXCOORD"
    COLOR = "COLOR"
    BLENDINDICES = "BLENDINDICES"
    TANGENT = "TANGENT"


class RIPHeader:
    magic_id = 0xDEADC0DE

    def __init__(self):
        self.magic = 0
        self.magic_s = 0
        self.version = 0
        self.face_count = 0
        self.vertex_count = 0
        self.vertex_size = 0
        self.texture_count = 0
        self.shader_count = 0
        self.attrib_count = 0
        self.attributes = []  # type: List[RIPAttribute]
        self.textures = []  # type: List[str]
        self.shaders = []  # type: List[str]
        self.indexes = []  # type: List[Tuple[int,int,int]]
        self.vertexes = [] # type: List[RIPVertex]


    def get_flat_verts(self):
        verts = []
        norms = []
        colors = []
        uvs = []
        for vert in self.vertexes:
            verts.append(vert.pos.as_Vector3D.as_list)
            uvs.append(vert.UV.as_Vector2D.as_list)
            norms.append(vert.norm.as_Vector3D.as_list)
            colors.append(vert.color.as_Vector3D.as_list)
        return verts,uvs,norms,colors

    def read(self, reader: ByteIO):
        self.magic = reader.read_uint32()
        self.magic_s = "%X" % self.magic
        self.version = reader.read_uint32()
        self.face_count = reader.read_uint32()
        self.vertex_count = reader.read_uint32()
        self.vertex_size = reader.read_uint32()
        self.texture_count = reader.read_uint32()
        self.shader_count = reader.read_uint32()
        self.attrib_count = reader.read_uint32()
        self.read_attributes(reader)
        self.read_textures(reader)
        self.read_shaders(reader)
        self.read_indexes(reader)
        self.read_vertexes(reader)

    def read_attributes(self, reader: ByteIO):
        for _ in range(self.attrib_count):
            attr = RIPAttribute()
            self.attributes.append(attr.read(reader))
            print("Found",attr.name,'attribute')

    def read_textures(self, reader: ByteIO):
        self.textures = [reader.read_ascii_string() for _ in range(self.texture_count)]

    def read_shaders(self, reader: ByteIO):
        self.shaders = [reader.read_ascii_string() for _ in range(self.shader_count)]

    def read_indexes(self, reader: ByteIO):
        self.indexes = [(reader.read_uint32(), reader.read_uint32(), reader.read_uint32()) for _ in
                        range(self.face_count)]

    def read_vertexes(self, reader: ByteIO):
        for i in range(self.vertex_count):
            vertex_entry = reader.tell()
            vertex = RIPVertex()
            for attrib in self.attributes:
                reader.seek(vertex_entry + attrib.offset)
                if attrib.name == RIPAttrTypes.POSITION:
                    vertex.pos.read(reader,attrib.types)
                elif attrib.name == RIPAttrTypes.NORMAL:
                    vertex.norm.read(reader,attrib.types)
                elif attrib.name == RIPAttrTypes.TEXCOORD:
                    vertex.UV.read(reader,attrib.types)
                elif attrib.name == RIPAttrTypes.COLOR:
                    vertex.color.read(reader,attrib.types)
                elif attrib.name == RIPAttrTypes.TANGENT:
                    reader.skip(attrib.size)
                elif attrib.name == RIPAttrTypes.BLENDINDICES:
                    vertex.blend.read(reader,attrib.types)
                else:
                    print('Found unknown attribute! Please report about this')
            reader.seek(vertex_entry + self.vertex_size)
            self.vertexes.append(vertex)


class RIPVector:
    def __init__(self):
        self.x, self.y, self.z = 0, 0, 0

    def read(self, reader: ByteIO):
        self.x, self.y, self.z = reader.read_fmt('fff')
        return self
    @property
    def as_list(self):
        return [self.x, self.y, self.z]

    def __repr__(self):
        return "<RIPVector 2D X:{0.x} Y:{0.y} Z:{0.z}>".format(self)

    @property
    def as_string(self):
        return "X:{0.x} Y:{0.y} Z:{0.z}>".format(self)

class RIPIntVector:
    def __init__(self):
        self.x, self.y, self.z = 0, 0, 0

    def read(self, reader: ByteIO):
        self.x, self.y, self.z = reader.read_fmt('iii')
        return self
    @property
    def as_list(self):
        return [self.x, self.y, self.z]

    def __repr__(self):
        return "<RIPVector 2D X:{0.x} Y:{0.y} Z:{0.z}>".format(self)

    @property
    def as_string(self):
        return "X:{0.x} Y:{0.y} Z:{0.z}>".format(self)

class RIPUIntVector:
    def __init__(self):
        self.x, self.y, self.z = 0, 0, 0

    def read(self, reader: ByteIO):
        self.x, self.y, self.z = reader.read_fmt('iii')
        return self

    @property
    def as_list(self):
        return [self.x, self.y, self.z]

    def __repr__(self):
        return "<RIPVector 2D X:{0.x} Y:{0.y} Z:{0.z}>".format(self)

    @property
    def as_string(self):
        return "X:{0.x} Y:{0.y} Z:{0.z}>".format(self)


class RIPVector2D:
    def __init__(self):
        self.x, self.y = 0, 0

    def read(self, reader: ByteIO):

        self.x,self.y,_,_ = reader.read_fmt('ffff')
        return self
    @property
    def as_list(self):
        return [self.x, self.y]

    def __repr__(self):
        return "<RIPVector 2D X:{0.x} Y:{0.y}>".format(self)

    @property
    def as_string(self):
        return "X:{0.x} Y:{0.y}>".format(self)
tt ={0:'f',1:'L',2:'l'}
class RIPVarVector:
    def __init__(self):
        self.values = []

    def read(self,reader:ByteIO,types):
        fmt = ''.join([tt.get(f, "L") for f in types])
        self.values = list(reader.read_fmt(fmt))

    @property
    def as_Vector3D(self):
        vec = RIPVector()
        self.values.extend([0] * 3)
        vec.x,vec.y,vec.z = self.values[:3]
        return vec
    @property
    def as_IntVector3D(self):
        vec = RIPIntVector()
        self.values.extend([0] * 3)
        vec.x,vec.y,vec.z = self.values[:3]
        return vec
    @property
    def as_Vector2D(self):
        vec = RIPVector2D()
        self.values.extend([0] * 3)
        vec.x,vec.y = self.values[:2]
        return vec

    def __repr__(self):
        return "RIPVarVector values:{0.values}".format(self)

class RIPVertex:
    def __init__(self):
        self.pos = RIPVarVector()
        self.norm = RIPVarVector()
        self.UV = RIPVarVector()
        self.color = RIPVarVector()
        self.blend = RIPVarVector()

    def __repr__(self):
        return "<RIPVertex 2D X:{0.x} Y:{0.y}>".format(self.pos)


class RIPAttribute:

    def __init__(self):
        self.name = ''
        self.index = 0
        self.offset = 0
        self.size = 0
        self.type_map_elements = 0
        self.types = []

    def read(self, reader: ByteIO):
        print("Attr entry",reader.tell())
        self.name = reader.read_ascii_string()
        print(self.name)
        self.index = reader.read_uint32()
        self.offset = reader.read_uint32()
        self.size = reader.read_uint32()
        print(reader.tell())
        self.type_map_elements = reader.read_uint32()
        self.types = [reader.read_uint32() for _ in range(self.type_map_elements)]
        print(self)
        return self

    def __repr__(self):
        return "<RIP attrib name:{0.name} index:{0.index} offset:{0.offset} size:{0.size} type map elements:{0.type_map_elements} types:{0.types}>".format(
            self)
