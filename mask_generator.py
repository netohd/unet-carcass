import json
from pathlib import Path

import numpy as np
from skimage import draw, io
from sklearn.preprocessing import label_binarize

IMAGES = Path("imgs/")
LABELS = Path("annots/")
TARGET = Path("masksV2/")

classes = ["background"]

# faz a verificacao de erros de ortografia
typos = {
    "backgroudn": "background",
    "not_defined": "background",
    "": "background",
}

x = 0
for annotations in LABELS.glob("*.json"):
    annotations = json.load(open(annotations))

    for entry in annotations.values():
        try:
            # certifica que tem pelo menos uma regiao
            entry["regions"]

            file = IMAGES / entry["filename"]
            other = (TARGET / entry["filename"]).with_suffix(f"{file.suffix}")
            image = io.imread(file)
            print(file)
        except:
            continue

        height, width, _ = image.shape

        mask = np.full((height, width), classes.index("background"), dtype=np.uint8)

        for region in entry["regions"]:
            try:
                region_class = region["region_attributes"]["regiao"].strip().lower()
                region_class = typos.get(region_class, region_class)

                if region_class == "inteira" or region_class == "inteiro":
                    continue

                if region_class not in classes:
                    classes.append(region_class)

                region_shape = region["shape_attributes"]["name"]

                if region_shape == "polygon" or region_shape == "polyline":
                    xs = region["shape_attributes"]["all_points_x"]
                    ys = region["shape_attributes"]["all_points_y"]

                    if region_shape == "polyline":
                        xs.append(xs[0])
                        ys.append(ys[0])

                    indices = draw.polygon2mask((height, width), list(zip(ys, xs)))
                elif region_shape == "circle":
                    cx = region["shape_attributes"]["cx"]
                    cy = region["shape_attributes"]["cy"]
                    r = region["shape_attributes"]["r"]

                    indices = draw.disk((cy, cx), r)
                elif region_shape == "ellipse":
                    cx = region["shape_attributes"]["cx"]
                    cy = region["shape_attributes"]["cy"]
                    rx = region["shape_attributes"]["rx"]
                    ry = region["shape_attributes"]["ry"]

                    indices = draw.ellipse(cy, cx, ry, rx)
                else:
                    print(region_shape, region["shape_attributes"])

                mask[indices] = classes.index(region_class)
            except:
                pass
        if x == 0:
            print(mask)
        io.imsave(other, mask, check_contrast=False)
    x += 1
print(classes)