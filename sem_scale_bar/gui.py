import os

from sem_scale_bar.core import process_file


def run_gui():
    import FreeSimpleGUI as sg

    sg.theme("NeonYellow1")  # window colours (theme); 'NeonGreen1' is fine, also

    layout = [
        [sg.B("Choose folder with SEM images"), sg.B("Choose one SEM image")],
        [
            sg.T("Background colour:"),
            sg.B("white", button_color=("orange", "gray"), tooltip="Default"),
            sg.B("black", button_color=(sg.theme_background_color())),
        ],
        [
            sg.T("Language:"),
            sg.B("English", button_color=("orange", "gray"), tooltip="Default"),
            sg.B("Russian", button_color=(sg.theme_background_color())),
        ],
        [
            sg.T("Location:"),
            sg.B("left", button_color=(sg.theme_background_color())),
            sg.B("right", button_color=("orange", "gray"), tooltip="Default"),
        ],
        [
            sg.T("Label on the image, e.g. 'a)' or 'B':"),
            sg.Input(size=(20, 1), key="-Label-"),
            sg.T("(can be empty)"),
        ],
        [
            sg.B("label: left", button_color=("orange", "gray"), tooltip="Default"),
            sg.B("label: right", button_color=(sg.theme_background_color())),
        ],
        [sg.Checkbox("Use standard 1-2-5 bar sizes", key="-StandardSizes-")],
        [sg.Push(), sg.B("Process"), sg.Push()],
        [sg.Output(size=(60, 10))],
        [sg.Push(), sg.B("Exit"), sg.Push()],
    ]

    window = sg.Window("SEM scale bar - version 4.2", layout)

    rect_color = "white"
    language = "English"
    corner = "right"
    label_corner = "left"
    label = ""
    use_standard_sizes = False

    chosen_color = "white"
    chosen_language = "English"
    chosen_corner = "right"
    chosen_label_corner = "label: left"

    k = 1  # index for processed images
    folder = None
    file = None

    while True:
        event, values = window.read()

        if event == "Choose folder with SEM images":
            folder = sg.popup_get_folder("Select a folder", no_window=True)

        if event == "Choose one SEM image":
            file = sg.popup_get_file("Select an image", no_window=True)

        if event in ["white", "black"]:
            rect_color = event
            if chosen_color:
                window[chosen_color].update(button_color=(sg.theme_background_color()))
            window[event].update(button_color=("orange", "gray"))
            chosen_color = event

        if event in ["English", "Russian"]:
            language = event
            if chosen_language:
                window[chosen_language].update(
                    button_color=(sg.theme_background_color())
                )
            window[event].update(button_color=("orange", "gray"))
            chosen_language = event

        if event in ["left", "right"]:
            corner = event
            if chosen_corner:
                window[chosen_corner].update(button_color=(sg.theme_background_color()))
            window[event].update(button_color=("orange", "gray"))
            chosen_corner = event

        if event in ["label: left", "label: right"]:
            label_corner = "left" if event.endswith("left") else "right"
            if chosen_label_corner:
                window[chosen_label_corner].update(
                    button_color=(sg.theme_background_color())
                )
            window[event].update(button_color=("orange", "gray"))
            chosen_label_corner = event

        try:
            label = values["-Label-"]
        except Exception:
            pass
        try:
            use_standard_sizes = values["-StandardSizes-"]
        except Exception:
            pass

        if event == "Process":
            if folder is not None:
                for root, _, files in os.walk(folder):
                    for file_name in files:
                        full_file_name = os.path.join(root, file_name)
                        process_file(
                            full_file_name,
                            language,
                            rect_color,
                            corner,
                            label,
                            label_corner,
                            k,
                            use_standard_sizes,
                        )
                k += 1
                folder = None
                print("Process is complete. Check initial folder.")
            elif file is not None:
                process_file(
                    file,
                    language,
                    rect_color,
                    corner,
                    label,
                    label_corner,
                    k,
                    use_standard_sizes,
                )
                k += 1
                file = None
                print("Process is complete. Check initial folder.")
            else:
                print("Choose folder or image.")
            window.refresh()

        if event == sg.WIN_CLOSED or event == "Exit":
            break

    window.close()
