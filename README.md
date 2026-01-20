# SEM_scale_bar
SEM_scale_bar is a software for fast processing of images obtained from scanning electron microscope (SEM). The software cuts an info-panel from the image and creates a scale bar according to the image's metadata.

SEM_scale_bar processed all SEM images that it finds in the folder for seconds. By default, English language, a white background for scale bar, and right-down corner are set (just press 'Process' if you don't want to change these settings). The "Label" input allows you to put a label on the SEM image in the upper left or right corner. The processed images are saved to the same folder where the original RAM images are located.

SEM_scale_bar is licensed under the General Public Licenses (GPL), which allows all users to use, share, and modify the software freely.

The current version (v4) works with SEM images ("tif" and "png" extensions) obtained from Tescan, Zeiss, LEO, SM-32, and, probably, FEI (Helios) microscopes. The result of LEO image processing must be carefully checked, errors may occur due to incomplete information in the metadata of the microscope of this brand.

The actual version of the software can be downloaded from our lab's web page (http://oxide.ru/?q=content/%D0%BF%D0%BE).

If you are going to publish SEM images processed using SEM_scale_bar in a scientific article, we will be glad if you mark the use of SEM_scale_bar in the "Acknowledgements" section.

## Command-line usage

Run the CLI directly:

```bash
python -m sem_scale_bar.cli /path/to/image_or_folder \
  --language English \
  --background-color white \
  --scale-bar-corner right \
  --label-text "a)" \
  --label-corner left \
  --output-index 1
```

Run the package entrypoint (GUI if available, otherwise CLI). Use `--headless` to force CLI mode:

```bash
python -m sem_scale_bar --headless /path/to/folder
```
