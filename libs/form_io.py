import json
JSON_EXT = '.json'


class FormReader:
    def __init__(self, filepath):
        self.shapes = []
        self.fields = []
        self.filepath = filepath
        self.verified = False
        try:
            self.parseJSON()
        except:
            pass

    def getShapes(self):
        return self.shapes

    def parseJSON(self):
        def to_shape(shape):
            if not shape:
                self.shapes.append((None, None, None, None, None, False))
                return
            xmin = int(float(shape['xmin']))
            ymin = int(float(shape['ymin']))
            xmax = int(float(shape['xmax']))
            ymax = int(float(shape['ymax']))
            points = [(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)]
            self.shapes.append(
                (shape['label'], shape['tag'], points, None, None, False))

        with open(self.filepath) as json_file:
            self.fields = json.load(json_file)
        for field in self.fields:
            to_shape(field['key'])
            to_shape(field['value'])


class FormWriter():
    def __init__(self,
                 foldername,
                 filename,
                 imgSize,
                 databaseSrc='Unknown',
                 localImgPath=None):
        self.foldername = foldername
        self.filename = filename
        self.databaseSrc = databaseSrc
        self.imgSize = imgSize
        self.fieldlist = []
        self.localImgPath = localImgPath
        self.verified = False

    def addField(self, key_label, key_tag, key_points, value_label, value_tag,
                 value_points):
        def gen_dict(label, tag, points):
            if not label or not points:
                return None
            return {
                'label': label,
                'tag': tag,
                'xmin': points[0],
                'ymin': points[1],
                'xmax': points[2],
                'ymax': points[3]
            }

        self.fieldlist.append({
            'key':
            gen_dict(key_label, key_tag, key_points),
            'value':
            gen_dict(value_label, value_tag, value_points)
        })

    def save(self, targetFile=None):
        if targetFile is None:
            targetFile = self.filename + JSON_EXT
        with open(targetFile, "w") as write_file:
            json.dump(self.fieldlist, write_file)
