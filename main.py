from textual.reactive import reactive
from textual.app import App, ComposeResult
from textual.containers import Container, Grid, Center
from textual.widget import Widget
from textual.screen import Screen, ModalScreen
from textual.widgets import Button, Input, Label, OptionList, Static, Header, Footer
from rich_pixels import Pixels  # pyright: ignore
from icons.read_icon import iconParser
from shutil import get_terminal_size
from geopy.geocoders import Nominatim  # pyright: ignore


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
            geolocator = Nominatim(user_agent="weatherTUI")
            location = geolocator.geocode(str(event.value))
            address = location.address.split(", ")
            address = f"{address[0]}, {address[1]} ({round(location.latitude, 2)}, {round(location.longitude, 2)})"

            self.query_one("#al-out", Label).update(address)


class Portrait(Screen):
    CSS_PATH = "layout.css"

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="split"):
            with Container(id="general"):
                yield Label("Weather for {location}", id="g-loc")
                with Container(id="g-ico"):
                    yield Label(iconParser().read()[2], id="g-ico-icon")
                yield Label("condition", id="g-cond")
                yield Label("detials", id="g-det")
                with Container(id="g-ext"):
                    yield Label("1")
                    yield Label("2")
                    yield Label("3")
            with Container(id="detailed"):
                for y in range(7):
                    for x in range(19):
                        yield Label(id=f"grid-{x}-{y}")
        yield Footer()

    def on_mount(self) -> None:
        # Types for detailed
        self.query_one("#grid-0-0", Label).update("Hours:")
        self.query_one("#grid-0-1", Label).update("Clouds:")
        self.query_one("#grid-0-2", Label).update("Visib:")
        self.query_one("#grid-0-3", Label).update("Fog:")
        self.query_one("#grid-0-4", Label).update("Precip:")
        self.query_one("#grid-0-5", Label).update("Wind:")
        self.query_one("#grid-0-6", Label).update("Temp:")


class Landscape(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()


class weatherPie(App):
    BINDINGS = [
        ("ctrl+w", "switch_mode('portrait')", "Portrait"),
        ("ctrl+e", "switch_mode('landscape')", "Landscape"),
        ("ctrl+c", "app.quit()", "Quit"),
        ("ctrl+a", "bind_push_screen('add-location')", "Add Location"),
        ("ctrl+s", "bind_push_screen('select-location')", "Select Location"),
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


if __name__ == "__main__":
    app = weatherPie()
    app.run()
