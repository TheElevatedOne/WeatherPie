import os
import os.path as op
import shutil
from textual_image.widget import Image


class iconParser:
    def __init__(self) -> None:
        self.cwd = op.abspath(op.dirname(__file__))
        self.im_dir = [
            x for x in os.listdir(op.join(self.cwd, "1024x")) if ".png" in x
        ]
        self.im_dir.sort()

    def load_icon(self, cond: int, is_day: bool) -> str:
        if cond <= 2:
            icon = [x for x in self.im_dir if f"{cond}_{int(is_day)}" in x][0]
        else:
            icon = [x for x in self.im_dir if f"{cond}" in x][0]

        return op.join(self.cwd, "1024x", icon)
