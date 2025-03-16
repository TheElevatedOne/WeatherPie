# Textual imports
from textual.reactive import reactive
from textual.app import App, ComposeResult
from textual.containers import Container, Grid, Center
from textual.screen import Screen, ModalScreen
from textual.widgets import Input, Label, OptionList, Header, Footer

# Icon imports
from icons.read_icon import iconParser
from textual_image.widget import Image

# Other imports
from shutil import get_terminal_size
from geopy.geocoders import Nominatim  # pyright: ignore

# API imports
from backend.co_parser import coParser
from backend.om_parser import omParser


class SelectLocation(ModalScreen):
    BINDINGS = [("ctrl+c", "app.pop_screen()", "Close"), ("shift+enter", "", "Confirm")]

    def compose(self) -> ComposeResult:
        yield Grid(
            Center(Label("[bold]Select Location[/bold]", id="sl-title")),
            OptionList("Default", id="sl-olist"),
            Footer(),
            id="selloc",
        )


class AddLocation(ModalScreen):
    BINDINGS = [("ctrl+c", "app.pop_screen()", "Close"), ("shift+enter", "", "Confirm")]

    def compose(self) -> ComposeResult:
        yield Grid(
            Center(Label("[bold]Add a New Location[/bold]", id="al-title")),
            Input(placeholder="Search", id="al-search"),
            Label(id="al-out"),
            Footer(),
            id="addloc",
        )

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.value != "":
            geolocator = Nominatim(user_agent="WeatherPie")
            location = geolocator.geocode(str(event.value))
            address = location.address.split(", ")
            address = f"{address[0]}, {address[1]} ({round(location.latitude, 2)}, {round(location.longitude, 2)})"

            self.query_one("#al-out", Label).update(address)


class Portrait(Screen):
    CSS_PATH = "layout.css"

    icon_parser = reactive(iconParser())
    m_ico = reactive(str)
    d1_ico = reactive(str)
    d2_ico = reactive(str)
    d3_ico = reactive(str)

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="split"):
            with Container(id="general"):
                yield Label("Weather for {location}", id="g-loc")
                with Container(id="g-ico"):
                    yield Image(id="g-ico-icon")
                yield Label("condition", id="g-cond")
                with Container(id="g-det"):
                    yield Label(id="skyq")
                    with Container(id="celeste"):
                        yield Label(id="sun")
                        yield Label(id="moon")
                        yield Label(id="night")
                with Container(id="g-ext"):
                    with Container(id="daily-1"):
                        yield Image(id="ico-1")
                        yield Label(id="day-1")
                    with Container(id="daily-2"):
                        yield Image(id="ico-2")
                        yield Label(id="day-2")
                    with Container(id="daily-3"):
                        yield Image(id="ico-3")
                        yield Label(id="day-3")
            with Container(id="detailed"):
                for y in range(7):
                    for x in range(19):
                        yield Label(id=f"grid-{x}-{y}")
        yield Footer()

    def gen_om_data(self, wdict: dict) -> None:
        c_weather = wdict["current"]
        d_weather = wdict["daily"]

        m_img = self.query_one("#g-ico-icon", Image)
        m_ico = self.icon_parser.load_icon(
            c_weather["weather-code"][0], c_weather["is-day"]
        )
        m_img.image = m_ico

        cond = self.query_one("#g-cond", Label)
        cond.update(f"""[b][u]{c_weather["weather-code"][1]}[/u][/b]

Temperature: [b]{c_weather["temperature"]}°C[/b]
Precipitation: [b]{c_weather["precipitation"]} mm[/b]
Humidity: {c_weather["rel-humidity"]}%

Wind Speed: [b]{c_weather["wind-speed"]} km/h[/b]
Wind Gusts: {c_weather["wind-gusts"]} km/h
Wind Direction: {c_weather["wind-dir"]}
        """)

        for key, value in d_weather.items():
            d_img = self.query_one(f"#ico-{int(key) + 1}", Image)
            d_ico = self.icon_parser.load_icon(value["code"][0], True)
            d_img.image = d_ico

            day = self.query_one(f"#day-{int(key) + 1}", Label)
            day.update(f"""[b][u]{value["code"][1]}[/u][/b]

[u]Date:[/u] [b]{value["date"].replace("/", "[/b]/")}

Temp (Max): [b]{value["temp-max"]}[/b]
Temp (Min): [b]{value["temp-min"]}[/b]
Prec: [b]{value["prec"]} mm[/b]""")

    def gen_co_data(self, wdict: dict) -> None:
        sun = wdict["day"]["sun"]
        moon = wdict["day"]["moon"]

        self.query_one("#sun", Label).update(f"""[#FFFF0F][b][u]Sun[/u][/b][/]

Rise: {sun["rise"]}
Set: {sun["set"]}""")

        self.query_one("#moon", Label).update(f"""[#D6D6D6][b][u]Moon[/u][/b][/]

Rise: {moon["rise"]}
Set: {moon["set"]}""")

        self.query_one(
            "#night", Label
        ).update(f"""[#98A2FF][b][u]Night Length[/u][/b][/]

Civil Dark: {sun["civil-dark"][0]} - {sun["civil-dark"][1]}
Nauti Dark: {sun["nautical-dark"][0]} - {sun["nautical-dark"][1]}
Astro Dark: {sun["astro-dark"][0]} - {sun["astro-dark"][1]}""")

        skyq = wdict["sky-quality"]
        self.query_one("#skyq", Label).update(f"""[u]Sky Quality[/u]

Bortle: [b]{skyq["bortle_class"]}[/b]
Magnitude: {skyq["magnitude"]}

Artificial  {skyq["artif-brightness"][0]}
Brightness: {skyq["artif-brightness"][1]}""")

        hours = wdict["day"]["hours"]
        hours = dict(list(hours.items())[:-6])
        colors = {
            "good": ["#109410", "#FFFFFF", "#19E419", "#92F392"],
            "ok": ["#B94600", "#FFFFFF", "#FF5D01", "#FFAA7A"],
            "bad": ["#980000", "#FFFFFF", "#FF1A1A", "#FF8585"],
        }

        for i, (h, v) in enumerate(hours.items()):
            hour = self.query_one(f"#grid-{i + 1}-0", Label)
            hour.update(f"[bold]{h}[/bold]")
            hour.styles.background = colors[v["conditions"]][0]
            hour.styles.color = colors[v["conditions"]][1]
            hour.styles.border = ("heavy", colors[v["conditions"]][3])
            hour.styles.border_top = ("round", colors[v["conditions"]][2])
            hour.styles.text_align = "center"

            clouds = self.query_one(f"#grid-{i + 1}-1", Label)
            clouds.update(v["clouds"])
            if int(v["clouds"]) >= 60:
                cl_color = colors["bad"]
            elif int(v["clouds"]) >= 35:
                cl_color = colors["ok"]
            else:
                cl_color = colors["good"]

            clouds.styles.background = cl_color[0]
            clouds.styles.color = cl_color[1]
            clouds.styles.border = ("heavy", cl_color[3])
            clouds.styles.border_top = ("round", cl_color[2])
            clouds.styles.border_bottom = ("round", cl_color[2])
            clouds.styles.text_align = "center"

            visib = self.query_one(f"#grid-{i + 1}-2", Label)
            visib.update(v["visibility"])
            if int(v["visibility"]) == 14:
                vi_color = colors["good"]
            elif int(v["visibility"]) >= 10:
                vi_color = colors["ok"]
            else:
                vi_color = colors["bad"]
            visib.styles.background = vi_color[0]
            visib.styles.color = vi_color[1]
            visib.styles.border = ("heavy", vi_color[3])
            visib.styles.border_top = ("round", vi_color[2])
            visib.styles.border_bottom = ("round", vi_color[2])
            visib.styles.text_align = "center"

            fog = self.query_one(f"#grid-{i + 1}-3", Label)
            fog.update(v["fog"])
            if int(v["fog"]) == 0:
                fog_color = colors["good"]
            elif int(v["fog"]) <= 25:
                fog_color = colors["ok"]
            else:
                fog_color = colors["bad"]
            fog.styles.background = fog_color[0]
            fog.styles.color = fog_color[1]
            fog.styles.border = ("heavy", fog_color[3])
            fog.styles.border_top = ("round", fog_color[2])
            fog.styles.border_bottom = ("round", fog_color[2])
            fog.styles.text_align = "center"

            prec = self.query_one(f"#grid-{i + 1}-4", Label)
            prec.update(v["prec-amount"])
            if float(v["prec-amount"]) == 0:
                pr_color = colors["good"]
            elif float(v["prec-amount"]) <= 3:
                pr_color = colors["ok"]
            else:
                pr_color = colors["bad"]
            prec.styles.background = pr_color[0]
            prec.styles.color = pr_color[1]
            prec.styles.border = ("heavy", pr_color[3])
            prec.styles.border_top = ("round", pr_color[2])
            prec.styles.border_bottom = ("round", pr_color[2])
            prec.styles.text_align = "center"

            wind = self.query_one(f"#grid-{i + 1}-5", Label)
            wind.update(v["wind"]["speed"])
            if int(v["wind"]["speed"]) > 15:
                wn_color = colors["bad"]
            elif int(v["wind"]["speed"]) > 7:
                wn_color = colors["ok"]
            else:
                wn_color = colors["good"]
            wind.styles.background = wn_color[0]
            wind.styles.color = wn_color[1]
            wind.styles.border = ("heavy", wn_color[3])
            wind.styles.border_top = ("round", wn_color[2])
            wind.styles.border_bottom = ("round", wn_color[2])
            wind.styles.text_align = "center"

            temp = self.query_one(f"#grid-{i + 1}-6", Label)
            temp.update(v["temperature"]["general"])
            if int(v["temperature"]["general"]) >= 35:
                tm_color = colors["bad"]
            elif int(v["temperature"]["general"]) >= 25:
                tm_color = colors["ok"]
            elif int(v["temperature"]["general"]) >= 0:
                tm_color = colors["good"]
            elif int(v["temperature"]["general"]) >= -10:
                tm_color = colors["ok"]
            else:
                tm_color = colors["bad"]
            temp.styles.background = tm_color[0]
            temp.styles.color = tm_color[1]
            temp.styles.border = ("heavy", tm_color[3])
            temp.styles.border_top = ("round", tm_color[2])
            temp.styles.text_align = "center"

    def on_mount(self) -> None:
        # Types for detailed
        types = ["Hours:", "Clouds:", "Visib:", "Fog:", "Precip:", "Wind:", "Temp:"]

        for row in range(7):
            x = self.query_one(f"#grid-0-{row}", Label)
            x.update(f"[u][b]{types[row]}[/b][/u]")
            x.styles.background = "#494949"
            x.styles.border = ("heavy", "#A3A3A3")
            x.styles.border_left = ("round", "#6F6F6F")

        self.co_api = coParser(lat="48.21", long="18.06", view="current")
        self.om_api = omParser(lat="48.21", long="18.06")

        self.gen_co_data(self.co_api.update())
        self.gen_om_data(self.om_api.update())


class Landscape(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()


class WeatherPie(App):
    BINDINGS = [
        ("ctrl+w", "switch_mode('portrait')", "Portrait"),
        ("ctrl+e", "switch_mode('landscape')", "Landscape"),
        ("ctrl+c", "app.quit()", "Quit"),
        ("ctrl+a", "bind_push_screen('add-location')", "Add Location"),
        ("ctrl+s", "bind_push_screen('select-location')", "Select Location"),
        ("ctrl+u", "update()", "Update"),
    ]
    MODES = {"portrait": Portrait, "landscape": Landscape}

    def on_mount(self) -> None:
        term = get_terminal_size()
        if term[0] > (3 * term[1]):
            self.switch_mode("landscape")
        else:
            self.switch_mode("portrait")

    def action_bind_push_screen(self, x: str) -> None:
        self.title = "WeatherPie"
        match x:
            case "add-location":
                self.push_screen(AddLocation())
            case "select-location":
                self.push_screen(SelectLocation())

    def action_update(self) -> None:
        pass


if __name__ == "__main__":
    app = WeatherPie()
    app.run()
