class BlockBase:
    def properties(self):
        return {}

class Facing(BlockBase):
    def properties(self):
        prop = super().properties()
        prop["facing"] = ["north", "east", "south", "west"]
        return prop
    
class Half(BlockBase):
    def properties(self):
        prop = super().properties()
        prop["half"] = ["bottom", "top"]
        return prop

class Shape(BlockBase):
    def properties(self):
        prop = super().properties()
        prop["shape"] = ["straight", "inner_left", "inner_right", "outer_left", "outer_right"]
        return prop

class Waterlogged(BlockBase):
    def properties(self):
        prop = super().properties()
        prop["waterlogged"] = ["true", "false"]
        return prop

class Open(BlockBase):
    def properties(self):
        prop = super().properties()
        prop["open"] = ["true", "false"]
        return prop

class Powered(BlockBase):
    def properties(self):
        prop = super().properties()
        prop["powered"] = ["true", "false"]
        return prop

class Face(BlockBase):
    def properties(self):
        prop = super().properties()
        prop["face"] = ["ceiling","floor","wall"]
        return prop
    


class Stair(Facing, Half, Shape, Waterlogged):
    def properties(self):
        return super().properties()
        

class Slab(Half):
    def properties(self):
        return super().properties()
    
class Wall(Facing):
    def properties(self):
        return super().properties()
    
class_registry = {
    "Stair": Stair,
    "Slab": Slab,
    "Normal": BlockBase,
    "Wall": Wall,
    # etc.
}
