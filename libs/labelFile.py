# Copyright (c) 2016 Tzutalin
# Create by TzuTaLin <tzu.ta.lin@gmail.com>

try:
    from PyQt5.QtGui import QImage
except ImportError:
    from PyQt4.QtGui import QImage

from base64 import b64encode, b64decode
from libs.pascal_voc_io import PascalVocWriter
from libs.form_io import FormWriter
from libs.yolo_io import YOLOWriter
from libs.form_io import JSON_EXT
import os.path
import sys


class LabelFileError(Exception):
    pass


class LabelFile(object):
    # It might be changed as window creates. By default, using XML ext
    # suffix = '.lif'
    suffix = JSON_EXT

    def __init__(self, filename=None):
        self.shapes = ()
        self.imagePath = None
        self.imageData = None
        self.verified = False

    def savePascalVocFormat(self,
                            filename,
                            shapes,
                            imagePath,
                            imageData,
                            lineColor=None,
                            fillColor=None,
                            databaseSrc=None):
        imgFolderPath = os.path.dirname(imagePath)
        imgFolderName = os.path.split(imgFolderPath)[-1]
        imgFileName = os.path.basename(imagePath)
        #imgFileNameWithoutExt = os.path.splitext(imgFileName)[0]
        # Read from file path because self.imageData might be empty if saving to
        # Pascal format
        image = QImage()
        image.load(imagePath)
        imageShape = [
            image.height(),
            image.width(), 1 if image.isGrayscale() else 3
        ]
        writer = PascalVocWriter(imgFolderName,
                                 imgFileName,
                                 imageShape,
                                 localImgPath=imagePath)
        writer.verified = self.verified

        for shape in shapes:
            points = shape['points']
            label = shape['label']
            tag = shape['tag']
            # Add Chris
            difficult = int(shape['difficult'])
            bndbox = LabelFile.convertPoints2BndBox(points)
            writer.addBndBox(bndbox[0], bndbox[1], bndbox[2], bndbox[3], label,
                             tag, difficult)

        writer.save(targetFile=filename)
        return

    def saveFormFormat(self,
                       filename,
                       fields,
                       imagePath,
                       imageData,
                       lineColor=None,
                       fillColor=None,
                       databaseSrc=None):
        def get_table(tables, shape_bbox):
            for table in tables:
                if encapsulated(table[0], shape_bbox):
                    return table
            return None

        def encapsulated(bbox1, bbox2):
            if bbox1[0] <= bbox2[0] and bbox1[1] <= bbox2[1] and bbox1[
                    2] >= bbox2[2] and bbox1[3] >= bbox2[3]:
                return True

        imgFolderPath = os.path.dirname(imagePath)
        imgFolderName = os.path.split(imgFolderPath)[-1]
        imgFileName = os.path.basename(imagePath)
        #imgFileNameWithoutExt = os.path.splitext(imgFileName)[0]
        # Read from file path because self.imageData might be empty if saving to
        # Pascal format
        image = QImage()
        image.load(imagePath)
        imageShape = [
            image.height(),
            image.width(), 1 if image.isGrayscale() else 3
        ]
        writer = FormWriter(imgFolderName,
                            imgFileName,
                            imageShape,
                            localImgPath=imagePath)
        writer.verified = self.verified

        tables = []
        for field in fields:
            value_points = field.value['points']
            value_label = field.value['label']
            value_tag = field.value['tag']
            value_bndbox = LabelFile.convertPoints2BndBox(value_points)
            if not field.key and value_tag == '#table#':
                tables.append((value_bndbox, value_label))
                writer.addTable(value_label, value_bndbox)

        for field in fields:
            value_points = field.value['points']
            value_label = field.value['label']
            value_tag = field.value['tag']
            value_bndbox = LabelFile.convertPoints2BndBox(value_points)
            if field.key:
                key_points = field.key['points']
                key_label = field.key['label']
                key_tag = field.key['tag']
                key_bndbox = LabelFile.convertPoints2BndBox(key_points)
                writer.addField(key_label, key_tag, key_bndbox, value_label,
                                value_tag, value_bndbox)
            elif value_tag != '#table#':
                table = get_table(tables, value_bndbox)
                if table:
                    writer.addCell(table[1], value_label, value_tag,
                                   value_bndbox)
                else:
                    writer.addField(None, None, None, value_label, value_tag,
                                    value_bndbox)

        writer.save(targetFile=filename)
        return

    def saveYoloFormat(self,
                       filename,
                       shapes,
                       imagePath,
                       imageData,
                       classList,
                       lineColor=None,
                       fillColor=None,
                       databaseSrc=None):
        imgFolderPath = os.path.dirname(imagePath)
        imgFolderName = os.path.split(imgFolderPath)[-1]
        imgFileName = os.path.basename(imagePath)
        #imgFileNameWithoutExt = os.path.splitext(imgFileName)[0]
        # Read from file path because self.imageData might be empty if saving to
        # Pascal format
        image = QImage()
        image.load(imagePath)
        imageShape = [
            image.height(),
            image.width(), 1 if image.isGrayscale() else 3
        ]
        writer = YOLOWriter(imgFolderName,
                            imgFileName,
                            imageShape,
                            localImgPath=imagePath)
        writer.verified = self.verified

        for shape in shapes:
            points = shape['points']
            label = shape['label']
            tag = shape['tag']
            # Add Chris
            difficult = int(shape['difficult'])
            bndbox = LabelFile.convertPoints2BndBox(points)
            writer.addBndBox(bndbox[0], bndbox[1], bndbox[2], bndbox[3], label,
                             difficult)

        writer.save(targetFile=filename, classList=classList)
        return

    def toggleVerify(self):
        self.verified = not self.verified

    ''' ttf is disable
    def load(self, filename):
        import json
        with open(filename, 'rb') as f:
                data = json.load(f)
                imagePath = data['imagePath']
                imageData = b64decode(data['imageData'])
                lineColor = data['lineColor']
                fillColor = data['fillColor']
                shapes = ((s['label'], s['points'], s['line_color'], s['fill_color'])\
                        for s in data['shapes'])
                # Only replace data after everything is loaded.
                self.shapes = shapes
                self.imagePath = imagePath
                self.imageData = imageData
                self.lineColor = lineColor
                self.fillColor = fillColor

    def save(self, filename, shapes, imagePath, imageData, lineColor=None, fillColor=None):
        import json
        with open(filename, 'wb') as f:
                json.dump(dict(
                    shapes=shapes,
                    lineColor=lineColor, fillColor=fillColor,
                    imagePath=imagePath,
                    imageData=b64encode(imageData)),
                    f, ensure_ascii=True, indent=2)
    '''

    @staticmethod
    def isLabelFile(filename):
        fileSuffix = os.path.splitext(filename)[1].lower()
        return fileSuffix == LabelFile.suffix

    @staticmethod
    def convertPoints2BndBox(points):
        xmin = float('inf')
        ymin = float('inf')
        xmax = float('-inf')
        ymax = float('-inf')
        for p in points:
            x = p[0]
            y = p[1]
            xmin = min(x, xmin)
            ymin = min(y, ymin)
            xmax = max(x, xmax)
            ymax = max(y, ymax)

        # Martin Kersner, 2015/11/12
        # 0-valued coordinates of BB caused an error while
        # training faster-rcnn object detector.
        if xmin < 1:
            xmin = 1

        if ymin < 1:
            ymin = 1

        return (int(xmin), int(ymin), int(xmax), int(ymax))
