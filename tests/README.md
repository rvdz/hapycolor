## Pretty display of image + palette
First, you need to generate the json file ```palettes.json``` that contains data of the path to each image and their corresponding palette.
To do this, use the ```-j``` option of hapycolor:

```python3 -m hapycolor -j -f <path/to/image>```

The json would be saved in a file called ```palettes.json```.

To generate the images:

```python3 tests/generate_image_palette.py -f palettes.json -d <output_directory>```
