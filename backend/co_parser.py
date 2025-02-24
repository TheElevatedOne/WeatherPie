from clear_outside_apy import ClearOutsideAPY


class coParser:
    def __init__(self, lat: str, long: str, view: str) -> None:
        "Initialize parser with default coords and view"
        self.view = view
        self.init = ClearOutsideAPY(lat, long, self.view)
        pass

    def update(self) -> dict:
        """
        Update and return parsed dictionary
        """
        full_dict = self.init.pull()
        day = full_dict["forecast"]["day-0"]
        hours = {}
        for i in day["hours"]:
            match day["hours"][i]["wind"]["direction"]:
                case "north":
                    wind = "⬇"
                case "west":
                    wind = "➡"
                case "south":
                    wind = "⬆"
                case "east":
                    wind = "⬅"
                case _:
                    if "south-east" in day["hours"][i]["wind"]["direction"]:
                        wind = "⬉"
                    elif "south-west" in day["hours"][i]["wind"]["direction"]:
                        wind = "⬈"
                    elif "north-east" in day["hours"][i]["wind"]["direction"]:
                        wind = "⬋"
                    else:
                        wind = "⬊"

            hours[i] = {
                "conditions": day["hours"][i]["conditions"],
                "clouds": day["hours"][i]["total-clouds"],
                "visibility": day["hours"][i]["visibility"],
                "fog": day["hours"][i]["fog"],
                "prec-prob": day["hours"][i]["prec-probability"],
                "prec-amount": day["hours"][i]["prec-amount"],
                "wind": {"speed": day["hours"][i]["wind"]["speed"], "direct": wind},
                "temperature": day["hours"][i]["temperature"],
                "humidity": day["hours"][i]["rel-humidity"],
            }
        ret_dict = {
            "sky-quality": full_dict["sky-quality"],
            "day": {"sun": day["sun"], "moon": day["moon"], "hours": hours},
        }
        return ret_dict

    def relocate(self, lat: str, long: str) -> None:
        "Switching to different location"
        self.init = ClearOutsideAPY(lat, long, self.view)
