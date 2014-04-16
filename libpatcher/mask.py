class MaskNotFoundError(Exception):
    "Thrown if mask was not found"
class AmbiguousMaskError(MaskNotFoundError):
    "Thrown if mask was found more than 1 time"

class Mask(object):
    "This class represents mask"
    def __init__(self, parts, offset=0, pos=None):
        """
        parts: list of alternating strings and integers.
            strings mean parts which will be matched,
            integers means "skip N bytes".
        offset: how many bytes from matched beginning to skip
        pos: parser.FilePos object describing block's (starting) position in file
        """
        self.parts = parts
        self.offset = offset
        self.pos = pos
        # TODO: validate
    def __repr__(self):
        def str2hex(s):
            if type(s) is int:
                return "?%d" % s
            else:
                return ' '.join(["%02X" % ord(c) for c in s])
        return "Mask at %s: %s @%d" % (self.pos, ','.join([str2hex(x) for x in self.parts]), self.offset)
    def match(self, data):
        """
        Tries to match this mask to given data.
        Returns matched position on success,
        False if not found
        or (exception?) if found more than one occurance.
        """
        # if mask starts with skip, append it to offset
        if type(self.parts[0]) is int:
            self.offset += self.parts[0]
            del self.parts[0]
        pos1 = data.find(self.parts[0])
        found = False
        while pos1 != -1:
            pos = pos1+len(self.parts[0])
            for p in self.parts[1:]:
                if type(p) is int:
                    pos += p
                else:
                    if p == data[pos:pos+len(p)]:
                        pos += len(p)
                    else:
                        break
            else: # not breaked -> matched
                if found is not False: # was already found? -> duplicate match
                    raise AmbiguousMaskError(self)
                found = pos1
            # and find next occurance:
            pos1 = data.find(self.parts[0], pos1+1)
        # all occurances checked
        if found is not False:
            return found + self.offset
        raise MaskNotFoundError(self)
    def getSize(self):
        """
        Returns size (in bytes) of the 'active' part of mask
        (excluding its part before @, or covered by initial ?-s)
        """
        return sum([len(x) if type(x) is str else x for x in self.parts]) - self.offset
    def getPos(self):
        return self.pos