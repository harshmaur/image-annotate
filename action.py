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
                                              ("Image files", "*.jpg *.jpeg *.png *.tiff *.tif *.bmp *.tbm")])

    if not image_paths:
        print("No images selected.")
        return False

    # Get footer text from user
    default_footer = os.path.basename(os.path.dirname(image_paths[0]))
    footer_text = simpledialog.askstring("Input", "Enter the footer text:\t\t\t\t\t\t\t\t", initialvalue=default_footer)

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
    root.title("Image Annotate")
    root.geometry("900x700")  # Increased window size for better aesthetics

    # Center the window on the primary screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    root.attributes('-topmost', True)
    root.update()
    root.attributes('-topmost', False)

    # Set a background color
    root.configure(bg="#e6f3ff")

    # Create a frame to center the content with a light blue background
    center_frame = tk.Frame(root, bg="#e6f3ff", padx=40, pady=40)
    center_frame.place(relx=0.5, rely=0.5, anchor="center")

    # Create and pack widgets with improved styling
    title_label = tk.Label(center_frame, text="Image Annotate", font=("Helvetica", 32, "bold"), bg="#e6f3ff", fg="#333333")
    title_label.pack(pady=30)

    description_label = tk.Label(center_frame, text="Bulk add text at the bottom of the images\nwith white border",
                                 wraplength=600, font=("Helvetica", 16), bg="#e6f3ff", fg="#555555")
    description_label.pack(pady=20)

    creator_label = tk.Label(center_frame, text="Created by - Harsh Maur", font=("Helvetica", 14, "italic"),
                             bg="#e6f3ff", fg="#777777")
    creator_label.pack(pady=30)

    def start_and_close():
        root.destroy()  # Close the splash screen
        start_processing()  # Start the processing

    start_button = tk.Button(center_frame, text="Start", command=start_and_close,
                             font=("Helvetica", 16, "bold"), padx=30, pady=15,
                             bg="#4CAF50", fg="white", activebackground="#45a049",
                             relief=tk.RAISED, bd=0)
    start_button.pack(pady=40)

    # Add hover effect to the button
    start_button.bind("<Enter>", lambda e: e.widget.config(bg="#45a049"))
    start_button.bind("<Leave>", lambda e: e.widget.config(bg="#4CAF50"))

    root.mainloop()

def start_processing():
    while True:
        if not process_batch():
            break

        if not messagebox.askyesno("Continue?", "Do you want to process another batch of images?"):
            break

    print("Image processing completed. Exiting.")


if __name__ == "__main__":
    main()
