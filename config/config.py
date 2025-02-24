import platform
from geopy.geocoders import Nominatim  # pyright: ignore
from configparser import ConfigParser


class Config:
    def __init__(self) -> None:
        self.config = ConfigParser()
        self.config.read("../weather.conf")
        pass

    def add_location(self, name: str, coord: str) -> None:
        self.config["Locations"][name] = coord
        with open("../weather.conf", "w") as cfg:
            self.config.write(cfg)

    def reload(self) -> None:
        self.config.read("../weather.conf")


if __name__ == "__main__":
    Config().add_location("a", '["b", "c"]')
