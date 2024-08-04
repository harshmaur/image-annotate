from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageOps

import tkinter
from tkinter import filedialog
import os
import csv
import platform

root = tkinter.Tk()
root.withdraw()
root.update()
INPUT_CSV_PATH = filedialog.askopenfilename(
    title="please select the csv file")
# INPUT_CSV_PATH = '/Users/harshmaur/Downloads/2A-87 Western Architecture - Final/test.csv'

root.update()
OUTPUT_DIR = filedialog.askdirectory(title="please select output folder")

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

        self.space_width = self.get_text_width(' ')

    def get_text_width(self, text):
        bbox = self.draw.textbbox((0, 0), text, font=self.font)
        return bbox[2] - bbox[0]

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
        ImageFont.FreeTypeFont: Font to draw text with.
    """
    width, height = image.size
    font_size = 50
    font = ImageFont.truetype(font_path, font_size)
    while (font.getbbox(text)[2] - font.getbbox(text)[0] + 1) < img_width_fraction * width and font_size < 60:
        font_size += 1
        font = ImageFont.truetype(font_path, font_size)
    return font


def trim(im):
    bg = Image.new(im.mode, im.size, im.getpixel((0, 0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)


with open(INPUT_CSV_PATH, 'r', encoding="utf-8-sig") as csvfile:
    spamreader = csv.DictReader(csvfile)
    for row in spamreader:
        print(row)
        img = Image.open(INPUT_CSV_PATH.replace(
            os.path.basename(INPUT_CSV_PATH), '')+row['Image Name'])
        img = trim(img)

        maxsize = (
            3000, int((float(img.size[1])*float(3000/float(img.size[0])))))
        img = img.resize(maxsize, Image.LANCZOS)
        img.thumbnail((3000, 3000), Image.LANCZOS)
        width, height = img.size

        bi = Image.new('RGB', (3500, 3500), 'white')
        bi.paste(img, (30, 200))
        footercaption = row.get('Footer')
        # splittling, then joining to get back name
        tname = ".".join(row.get('Image Name', '').split(".")[:-1])

        if (platform.system() == 'Darwin'):
            font = get_font(img, footercaption,
                            '/Library/Fonts/Arial.ttf', 0.8)
        elif (platform.system() == 'Windows'):
            font = get_font(img, footercaption,
                            r'C:\Windows\Fonts\Arial.ttf', 0.8)
        elif (platform.system() == 'Linux'):
            font = get_font(img, footercaption,
                            '/usr/share/fonts/truetype/freefont/FreeSans.ttf', 0.8)
        else:
            font = get_font(img, footercaption,
                            r'C:\Windows\Fonts\Arial.ttf', 0.8)
        draw = ImageDraw.Draw(bi)
        wrapped_footer_text = TextWrapper(
            footercaption, font, width).wrapped_text()

        draw.text((30, height+200), wrapped_footer_text,
                  font=font, fill="black")

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
