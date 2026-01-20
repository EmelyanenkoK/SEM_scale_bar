import os

import numpy as np
import png
import tifffile
from PIL import Image, ImageDraw, ImageFont

__all__ = [
    "extract_png_chunks",
    "get_scale",
    "cut_panel",
    "tif2np",
    "png2np",
    "get_tags_from_tiff",
    "get_bar",
    "draw_bar",
    "process_file",
]


def extract_png_chunks(filename):
    reader = png.Reader(filename)
    chunks = []
    for chunk_type, chunk_data in reader.chunks():
        chunks.append((chunk_type, chunk_data))
    return chunks


def get_scale(tags):
    pixel_size = 0  # for debugging
    if "CZ_SEM" in tags:
        try:  # for Zeiss images
            length = tags["CZ_SEM"]["ap_image_pixel_size"][2]
            if length == "nm":
                pixel_size = float(
                    tags["CZ_SEM"]["ap_image_pixel_size"][1] / 1000
                )  # microns per pixel
            else:  # length == 'pm':
                pixel_size = float(
                    tags["CZ_SEM"]["ap_image_pixel_size"][1] / 1000000
                )  # microns per pixel
        except:  # for LEO images
            n = tags["ImageWidth"] / 1024  # to recalculate image resolution in meter per pixel
            pixel_size = float(tags["CZ_SEM"][""][3] * 1000000) / n  # microns per pixel

    elif "50431" in tags:
        text = tags["50431"].split()  # for Tescan images
        for j in range(len(text)):
            find_pixel_size = str(text[j]).find("PixelSizeX")
            if find_pixel_size != -1:
                pixel_size = (
                    float(str(text[j]).split("=")[1].strip("'")) * 1000000
                )  # microns per pixel
                break

    elif "FEI_HELIOS" in tags:  # for FEI and SM-32 images
        if "¦" in tags["FEI_HELIOS"]["Beam"]["HFW"]:
            pixel_size = (
                float(tags["FEI_HELIOS"]["Beam"]["HFW"].split("¦")[0])
                / tags["ImageWidth"]
            )  # microns per pixel
        else:
            pixel_size = (
                float(tags["FEI_HELIOS"]["Beam"]["HFW"].split("mm")[0])
                / tags["ImageWidth"]
                * 1000
            )  # microns per pixel

    else:
        try:
            if b"gIFx" in tags[1]:  # metadata in png-image from Tescan microscope
                text = tags[1][1].split()
                for j in range(len(text)):
                    find_pixel_size = str(text[j]).find("PixelSizeX")
                    if find_pixel_size != -1:
                        pixel_size = (
                            float(str(text[j]).split("=")[1].strip("'")) * 1000000
                        )  # microns per pixel
                        break
        except:
            print("Unknown metadata format")

    return pixel_size


def cut_panel(img, tags):
    height, width = img.shape[:2]
    if "CZ_SEM" in tags:
        i = 0
        if "ap_image_pixel_size" in tags["CZ_SEM"]:  # for Zeiss images
            for row in img:
                if np.all(
                    row[2 : row.size - 3] == img[-2][2 : row.size - 3]
                ):  # img[-2] is a lower part of the infopanel frame; we want to find the upper part of the frame
                    strip_pixel_size = height - i
                    break
                i += 1
        else:  # for LEO images
            black_row = np.zeros(width - 6)
            for row in img:
                if np.all(black_row == row[3 : row.size - 3]):
                    strip_pixel_size = height - i
                    break
                i += 1

    elif "50431" in tags:
        text = tags["50431"].split()  # for Tescan images
        for j in range(len(text)):
            start_strip = str(text[j]).find(
                "ImageStripSize"
            )  # Tescan writes the infopanel height (in pixels) to the metadata parameter "ImageStripSize"
            if start_strip != -1:
                strip_pixel_size = int(str(text[j]).split("=")[1].strip("'"))
                break

    elif "FEI_HELIOS" in tags:  # for FEI and SM-32 images
        short_height = tags["FEI_HELIOS"]["Scan"]["ResolutionY"]
        full_height = tags["ImageLength"]
        strip_pixel_size = full_height - short_height

    else:
        try:
            if b"gIFx" in tags[1]:  # metadata in png-image from Tescan microscope
                text = tags[1][1].split()
                for j in range(len(text)):
                    start_strip = str(text[j]).find(
                        "ImageStripSize"
                    )  # Tescan writes the infopanel height (in pixels) to the metadata parameter "ImageStripSize"
                    if start_strip != -1:
                        strip_pixel_size = int(str(text[j]).split("=")[1].strip("'"))
                        break
        except:
            print(
                "Unknown metadata format. Only Zeiss, Tescan or LEO SEM initial images can be processed."
            )

    h = height - strip_pixel_size
    crop = img[0:h, 0:width]

    return crop


def tif2np(tif, name):
    img = tif.pages[0].asarray()
    if len(img.shape) > 2:
        img = img.mean(axis=0)
    assert len(img.shape) == 2
    if img.max() > 255:
        img = img / 255
    return img.astype(np.float32)


def png2np(filename):
    reader = png.Reader(filename)
    _, _, pixels, _ = reader.read()
    img = np.vstack([row for row in pixels])
    if len(img.shape) > 2:
        img = img.mean(axis=0)
    assert len(img.shape) == 2
    if img.max() > 255:
        img = img / 255
    return img.astype(np.float32)


def get_tags_from_tiff(tif):
    tif_tags = {}
    for tag in tif.pages[0].tags.values():
        name, value = tag.name, tag.value
        tif_tags[name] = value
    return tif_tags


def get_bar(img, pixel_size, lang):
    _, width = img.shape[:2]
    bar = width * pixel_size / 6  # bar lenght is about 1/6 of image width, microns, not an integer
    if bar >= 0.55:
        if bar >= 100:
            bar = round(bar / 100) * 100
        elif 100 > bar >= 10:
            bar = round(bar / 10) * 10
        else:
            bar = round(bar)
        bar_pixel_size = bar / pixel_size
        if lang == "Russian":
            scale = "мкм"
        else:
            scale = "\u03BCm"

    else:
        if bar >= 0.1:
            bar = round(bar * 10) * 100
        else:
            bar = round(bar * 100) * 10
        bar_pixel_size = bar / (pixel_size * 1000)
        if lang == "Russian":
            scale = "нм"
        else:
            scale = "nm"

    return (bar, bar_pixel_size, scale)


def draw_bar(img, tags, lang, rect_color, corner, label, label_corner):
    img1 = Image.fromarray(img)
    img1 = img1.convert("RGB")
    img2 = ImageDraw.Draw(img1)
    height = img.shape[0]

    pixel_size = get_scale(tags)
    bar_data = get_bar(img, pixel_size, lang)
    bar = round(bar_data[1])
    scale_text = f"{bar_data[0]} {bar_data[2]}"

    n = img.shape[1] / 2048  # make font size and bar size match image size
    font_size = round(80 * n)
    font = ImageFont.truetype("arial.ttf", font_size)
    text_length = img2.textlength(scale_text, font=font)
    bbox = img2.textbbox((0, 0), scale_text, font=font)
    text_height = bbox[3] - bbox[1]

    label_box = img2.textbbox((0, 0), label, font=font)
    label_text_height = label_box[3] - label_box[1] + round(40 * n)

    rect_height = text_height + round(67 * n)
    rect_width = bar + round(45 * n)  # bar width, pixels

    if rect_color == "black":
        bar_color = "white"
    else:
        bar_color = "black"

    if corner == "right":
        width = img.shape[1]
        # draw filled rectangle at the down right corner
        img2.rectangle(
            [
                (width - rect_width, height - rect_height),  # left upside corner
                (width, height),  # right downside corner
            ],
            fill=rect_color,
            outline=rect_color,
        )
    else:
        width = 0
        # draw filled rectangle at the down left corner
        img2.rectangle(
            [
                (0, height - rect_height),  # left upside corner
                (rect_width, height),  # right downside corner
            ],
            fill=rect_color,
            outline=rect_color,
        )

    # draw contrast bar in the rectangle
    img2.line(
        [
            (abs(width - bar - round(20 * n)), height - round(30 * n)),
            (abs(width - round(20 * n)), height - round(30 * n)),
        ],
        fill=bar_color,
        width=round(20 * n),
    )

    # label box
    if label != "":
        if label_corner == "left":
            # draw filled rectangle at the up left corner
            label_width = 0
            x_label = round(50 * n) / 2
            img2.rectangle(
                [
                    (0, 0),  # left upside corner
                    (label_box[2] + round(50 * n), label_text_height),  # right downside corner
                ],
                fill=rect_color,
                outline=rect_color,
            )
        else:
            label_width = img.shape[1]
            x_label = label_width - label_box[2] - round(50 * n) / 2
            # draw filled rectangle at the up right corner
            img2.rectangle(
                [
                    (label_width - label_box[2] - round(50 * n), 0),  # left upside corner
                    (label_width, label_text_height),  # right downside corner
                ],
                fill=rect_color,
                outline=rect_color,
            )

    x = abs(width - rect_width / 2) - text_length / 2
    y = height - rect_height

    # draw scale text
    img2.text(
        (x, y),
        scale_text,
        fill=bar_color,
        font=ImageFont.truetype("arial.ttf", font_size),
    )

    # draw label text
    if label != "":
        img2.text(
            (x_label, 0),
            label,
            fill=bar_color,
            font=ImageFont.truetype("arial.ttf", font_size),
        )

    return img1


# read full file path, process file (read tif metadata, cut panel, draw scale bar) and save result
def process_file(full_file_name, lan, rect_color, corner, label, label_corner, k):
    folder, filename_ext = os.path.split(full_file_name)
    short_file_name, extension = os.path.splitext(filename_ext)
    _, extension = extension.split(".")
    if extension == "tif" or extension == "TIF" or extension == "tiff":
        try:
            tif = tifffile.TiffFile(full_file_name)
            img = tif2np(tif, full_file_name)
            tif_tags = get_tags_from_tiff(tif)
            img_cropped = cut_panel(img, tif_tags)
            result = draw_bar(
                img_cropped, tif_tags, lan, rect_color, corner, label, label_corner
            )
            result.save(f"{folder}/{short_file_name}_cut_{k}.{extension}")
        except:
            print("Error during procession ", full_file_name, ".")

    elif extension == "png" or extension == "PNG":
        try:
            img = png2np(full_file_name)
            chunks = extract_png_chunks(full_file_name)  # = tif_tags for png
            img_cropped = cut_panel(img, chunks)
            result = draw_bar(
                img_cropped, chunks, lan, rect_color, corner, label, label_corner
            )
            result.save(f"{folder}/{short_file_name}_cut_{k}.{extension}")
        except:
            print("Error during procession ", full_file_name, ".")

    else:
        print(
            "File ",
            short_file_name,
            extension,
            " extension isn't 'tif' ('tiff'); it can't be processed.",
        )
