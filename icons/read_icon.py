import os
import shutil
from PIL import Image
from rich_pixels import Pixels


class iconParser:
    def __init__(self) -> None:
        self.cdir = os.path.abspath(os.path.dirname(__file__))
        self.im_dir = [x for x in os.listdir(self.cdir) if ".png" in x]
        self.im_dir.sort()
        pass

    def read(self) -> list:
        term_size = shutil.get_terminal_size()
        icon_size = round(term_size[0] / 4) - 2

        results = []
        for img in self.im_dir:
            pimg = Image.open(os.path.join(self.cdir, img))
            pimg = pimg.resize((icon_size, icon_size), Image.Resampling.NEAREST)

            px = Pixels.from_image(pimg)
            results.append(px)

        return results
