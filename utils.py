import os


def is_pdf(filename):
    return filename.lower().endswith(".pdf")


def is_image(filename):
    image_extensions = (
        ".jpg",
        ".jpeg",
        ".png"
    )

    return filename.lower().endswith(image_extensions)


def read_css():

    if os.path.exists("style.css"):

        with open("style.css") as css:

            return css.read()

    return ""