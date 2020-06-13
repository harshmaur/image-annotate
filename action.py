from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageOps

import Tkinter
import tkFileDialog
import os
import csv
import textwrap
import platform

root = Tkinter.Tk()
root.withdraw()
root.update()
INPUT_CSV_PATH = tkFileDialog.askopenfilename(
    title="please select the csv file")
# INPUT_CSV_PATH = '/Users/harshmaur/Downloads/2A-87 Western Architecture - Final/test.csv'

root.update()
OUTPUT_DIR = tkFileDialog.askdirectory(title="please select output folder")

root.update()
# OUTPUT_DIR = '/Users/harshmaur/Downloads/2A-87 Western Architecture - Final/testfolder'

# print INPUT_CSV_PATH, OUTPUT_DIR


class TextWrapper(object):
    """ Helper class to wrap text in lines, based on given text, font
        and max allowed line width.
    """

    def __init__(self, text, font, max_width):
        self.text = text
        self.text_lines = [
            ' '.join([w.strip() for w in l.split(' ') if w])
            for l in text.split('\n')
            if l
        ]
        self.font = font
        self.max_width = max_width

        self.draw = ImageDraw.Draw(
            Image.new(
                mode='RGB',
                size=(100, 100)
            )
        )

        self.space_width = self.draw.textsize(
            text=' ',
            font=self.font
        )[0]

    def get_text_width(self, text):
        return self.draw.textsize(
            text=text,
            font=self.font
        )[0]

    def wrapped_text(self):
        wrapped_lines = []
        buf = []
        buf_width = 0

        for line in self.text_lines:
            for word in line.split(' '):
                word_width = self.get_text_width(word)

                expected_width = word_width if not buf else \
                    buf_width + self.space_width + word_width

                if expected_width <= self.max_width:
                    # word fits in line
                    buf_width = expected_width
                    buf.append(word)
                else:
                    # word doesn't fit in line
                    wrapped_lines.append(' '.join(buf))
                    buf = [word]
                    buf_width = word_width

            if buf:
                wrapped_lines.append(' '.join(buf))
                buf = []
                buf_width = 0

        return '\n'.join(wrapped_lines)


def get_font(image, text, font_path, img_width_fraction):
    """
    Get desired font for image.

    Args:
        image (Image.Image): Image being drawn on.
        text (str): Text being drawn.
        font_path (str): Path to font.
        img_width_fraction (float): Fraction of image's width that text's width should be.

    Returns:
        ImageFont.Font: Font to draw text with.
    """
    width, height = image.size
    font_size = 50
    font = ImageFont.truetype(font_path, font_size)
    # +1 is to ensure font size is below requirement
    while (font.getsize(text)[0]+1) < img_width_fraction*width and font_size < 60:
        font_size += 1
        # print font_size
        font = ImageFont.truetype(font_path, font_size)
    return font


def trim(im):
    bg = Image.new(im.mode, im.size, im.getpixel((0, 0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)


with open(INPUT_CSV_PATH, 'r') as csvfile:
    spamreader = csv.DictReader(csvfile)
    for row in spamreader:
        img = Image.open(INPUT_CSV_PATH.replace(
            os.path.basename(INPUT_CSV_PATH), '')+row['Image Name'])
        img = trim(img)

        maxsize = (
            3000, int((float(img.size[1])*float(3000/float(img.size[0])))))
        img = img.resize(maxsize, Image.ANTIALIAS)
        img.thumbnail((3000, 3000), Image.ANTIALIAS)
        width, height = img.size

        bi = Image.new('RGB', (3500, 3500), 'white')
        bi.paste(img, (30, 200))
        footercaption = row.get('Footer') 
        tname = ".".join(row.get('Image Name', '').split(".")[:-1]) # splittling, then joining to get back name
        headercaption = []
        headercaption.append(row.get('Category', ''))
        headercaption.append(row.get('Almirah Loc', '') +
                             '-'+row.get('Accession Number', ''))
        headercaption.append(tname)
        headercaption.append(row.get('Book Name', ''))
        headercaption.append(row.get('Author', ''))
        headercaption = "/".join(list(filter(None, headercaption)))
        print headercaption
        if(platform.system() == 'Darwin'):
            font = get_font(img, headercaption,
                            '/Library/Fonts/Arial.ttf', 0.8)
        else:
            font = get_font(img, headercaption,
                            'C:\Windows\Fonts\Arial.ttf', 0.8)
        draw = ImageDraw.Draw(bi)
        wrapped_footer_text = TextWrapper(
            footercaption, font, width).wrapped_text()
        wrapped_header_text = TextWrapper(
            headercaption, font, width).wrapped_text()

        draw.text((30, height+200), wrapped_footer_text,
                  font=font, fill="black")

        startheight = 100/len(wrapped_header_text.splitlines())

        draw.text((30, startheight), wrapped_header_text,
                  font=font, fill='black')

        bi = trim(bi)

        newwidth, newheight = bi.size
        newbi = Image.new('RGB', (newwidth+60, newheight+60), 'white')
        newbi.paste(bi, (30, 30))

        name = row['Image Name'].replace(".tiff", "").replace(".TIFF", "").replace(
            ".TIF", "").replace(".JPEG", "").replace(".JPG", "").replace(".jpeg", "").replace(".jpg", "")

        # try:
        #     os.makedirs(OUTPUT_DIR + "/jpg/")
        # except OSError:
        #     if not os.path.isdir(OUTPUT_DIR + "/jpg/"):
        #         raise
        # try:
        #     os.makedirs(OUTPUT_DIR + "/pdf/")
        # except OSError:
        #     if not os.path.isdir(OUTPUT_DIR + "/pdf/"):
        #         raise
        newbi.save(OUTPUT_DIR + "/" +
                   name + '.jpg', format='JPEG', quality=95)
        # newbi.save(OUTPUT_DIR + "/jpg/" +
        #            name + '.jpg', format='JPEG', quality=95)
        # newbi.save(OUTPUT_DIR + "/pdf/" +
        #            name + '.pdf', format='PDF', resoultion=100.0)
        # newbi.show()
