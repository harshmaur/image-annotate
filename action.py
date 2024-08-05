from PIL import Image, ImageDraw, ImageFont, ImageChops
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import os
import platform


def get_font(image, text, font_path, img_width_fraction):
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


class TextWrapper:
    def __init__(self, text, font, max_width):
        self.text = text
        self.text_lines = [' '.join(
            [w.strip() for w in l.split(' ') if w]) for l in text.split('\n') if l]
        self.font = font
        self.max_width = max_width
        self.draw = ImageDraw.Draw(Image.new('RGB', (100, 100)))
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
                expected_width = word_width if not buf else buf_width + self.space_width + word_width
                if expected_width <= self.max_width:
                    buf_width = expected_width
                    buf.append(word)
                else:
                    wrapped_lines.append(' '.join(buf))
                    buf = [word]
                    buf_width = word_width
            if buf:
                wrapped_lines.append(' '.join(buf))
                buf = []
                buf_width = 0
        return wrapped_lines


def process_image(image_path, footer_text):
    img = Image.open(image_path)
    img = trim(img)

    maxsize = (3000, int((float(img.size[1])*float(3000/float(img.size[0])))))
    img = img.resize(maxsize, Image.LANCZOS)
    img.thumbnail((3000, 3000), Image.LANCZOS)
    width, height = img.size

    bi = Image.new('RGB', (3500, 3500), 'white')
    bi.paste(img, (30, 200))

    if platform.system() == 'Darwin':
        font_path = '/Library/Fonts/Arial.ttf'
    elif platform.system() == 'Windows':
        font_path = r'C:\Windows\Fonts\Arial.ttf'
    elif platform.system() == 'Linux':
        font_path = '/usr/share/fonts/truetype/freefont/FreeSans.ttf'
    else:
        font_path = r'C:\Windows\Fonts\Arial.ttf'

    font = get_font(img, footer_text, font_path, 0.8)
    draw = ImageDraw.Draw(bi)
    wrapped_footer_lines = TextWrapper(footer_text, font, width).wrapped_text()

    line_height = font.getbbox('A')[3] - font.getbbox('A')[1]
    total_text_height = len(wrapped_footer_lines) * line_height

    y = height + 200

    for line in wrapped_footer_lines:
        line_width = draw.textbbox((0, 0), line, font=font)[2]
        x = (width - line_width) // 2 + 30

        draw.text((x, y), line, font=font, fill="black")
        y += line_height

    bi = trim(bi)

    newwidth, newheight = bi.size
    newbi = Image.new('RGB', (newwidth+60, newheight+60), 'white')
    newbi.paste(bi, (30, 30))

    return newbi


def process_batch():
    # Select multiple image files
    image_paths = filedialog.askopenfilenames(title="Select image files", filetypes=[
                                              ("Image files", "*.jpg *.jpeg *.png *.tiff *.tif")])

    if not image_paths:
        print("No images selected.")
        return False

    # Get footer text from user
    footer_text = simpledialog.askstring("Input", "Enter the footer text:")

    if footer_text is None:
        print("No footer text entered.")
        return False

    # Process each image
    for image_path in image_paths:
        processed_image = process_image(image_path, footer_text)

        # Overwrite the original image
        processed_image.save(image_path, format='JPEG', quality=95)
        print(f"Processed and overwritten: {image_path}")

    print("All images in this batch have been processed and overwritten.")
    return True


def main():
    root = tk.Tk()
    root.withdraw()

    while True:
        if not process_batch():
            break

        if not messagebox.askyesno("Continue?", "Do you want to process another batch of images?"):
            break

    print("Image processing completed. Exiting.")


if __name__ == "__main__":
    main()
