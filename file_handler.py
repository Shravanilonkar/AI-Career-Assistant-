import os

TEMP_FOLDER = "temp"


def save_uploaded_file(uploaded_file):
    """
    Save uploaded file into temp folder.
    """

    os.makedirs(TEMP_FOLDER, exist_ok=True)

    file_path = os.path.join(
        TEMP_FOLDER,
        uploaded_file.name
    )

    with open(file_path, "wb") as file:
        file.write(uploaded_file.getbuffer())

    return file_path