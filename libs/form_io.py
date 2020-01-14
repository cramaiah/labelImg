import json
import re
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
            xmin = int(float(shape['bbox']['xmin']))
            ymin = int(float(shape['bbox']['ymin']))
            xmax = int(float(shape['bbox']['xmax']))
            ymax = int(float(shape['bbox']['ymax']))
            points = [(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)]
            self.shapes.append(
                (shape['label'], shape['tag'], points, None, None, False))

        with open(self.filepath) as json_file:
            json_str = json.load(json_file)
        self.fields = json_str['Fields']
        for table in json_str['Tables']:
            table['tag'] = '#table#'
            for cell in table['Cells']:
                self.fields.append({'key': None, 'value': cell})
            self.fields.append({'key': None, 'value': table})
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
        self.tableList = []
        self.localImgPath = localImgPath
        self.verified = False

    def addTable(self, value_label, value_points):
        self.tableList += [{
            'label': value_label,
            'bbox': {
                'xmin': value_points[0],
                'ymin': value_points[1],
                'xmax': value_points[2],
                'ymax': value_points[3],
            },
            'Cells': []
        }]

    def addCell(self, table_label, value_label, value_tag, value_points):
        row, col = re.search(r'r*(\d+)c*(\d+)*', value_tag).group(1, 2)
        for table in self.tableList:
            if table['label'] == table_label:
                table['Cells'].append({
                    'label': value_label,
                    'tag': value_tag,
                    'row': row,
                    'col': col,
                    'bbox': {
                        'xmin': value_points[0],
                        'ymin': value_points[1],
                        'xmax': value_points[2],
                        'ymax': value_points[3]
                    }
                })

    def addField(self, key_label, key_tag, key_points, value_label, value_tag,
                 value_points):
        def gen_dict(label, tag, points):
            if not label or not points:
                return None
            return {
                'label': label,
                'tag': tag,
                'bbox': {
                    'xmin': points[0],
                    'ymin': points[1],
                    'xmax': points[2],
                    'ymax': points[3]
                }
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

        metadata = {'filename': targetFile, 'image_dims': str(self.imgSize)}
        metadata.update({'Fields': self.fieldlist})
        metadata.update({'Tables': self.tableList})
        with open(targetFile, "w") as write_file:
            json.dump(metadata, write_file)
