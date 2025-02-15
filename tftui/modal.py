from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Grid
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    RichLog,
    Input,
    Checkbox,
    Static,
    DataTable,
    OptionList,
)
from textual.containers import Horizontal, Vertical


class WorkspaceModal(ModalScreen):
    workspaces = []
    current = ""
    options = None

    def __init__(self, workspaces: list, current: str, *args, **kwargs):
        self.current = current
        self.workspaces = workspaces
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        question = Static(
            Text("Select workspace to switch to:\n", "bold"),
            id="question",
        )
        self.options = OptionList(*self.workspaces)
        self.options.highlighted = self.workspaces.index(self.current)
        yield Vertical(
            question,
            self.options,
            Button("OK", id="ok"),
            id="workspaces",
        )

    def on_key(self, event) -> None:
        if event.key == "enter":
            self.dismiss(self.workspaces[self.options.highlighted])
        elif event.key == "escape":
            self.dismiss(None)


class FullTextModal(ModalScreen):
    contents = None
    is_resource = False

    def __init__(self, contents: str, is_resource: bool, *args, **kwargs):
        self.contents = contents
        self.is_resource = is_resource
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        fullscreen = RichLog(auto_scroll=False)
        if self.is_resource:
            fullscreen.highlight = True
            fullscreen.markup = True
            fullscreen.wrap = True

        fullscreen.write(self.contents)
        yield fullscreen

    def on_key(self, event) -> None:
        if event.key in ("f", "escape"):
            self.app.pop_screen()


class YesNoModal(ModalScreen):
    contents = None

    def __init__(self, contents: str, *args, **kwargs):
        self.contents = contents
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        question = RichLog(id="question", auto_scroll=False, wrap=True)
        question.write(self.contents)
        yield Grid(
            question,
            Button("Yes", variant="primary", id="yes"),
            Button("No", id="no"),
            id="yesno",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "yes":
            self.dismiss(True)
        else:
            self.dismiss(False)

    def on_key(self, event) -> None:
        if event.key == "y":
            self.dismiss(True)
        elif event.key == "n" or event.key == "escape":
            self.dismiss(False)


class PlanInputsModal(ModalScreen):
    input = None
    checkbox = None
    var_file = None

    def __init__(self, var_file, targets=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.var_file = var_file
        self.input = Input(id="varfile", placeholder="Optional")
        self.checkbox = Checkbox(
            "Target only selected resources",
            id="plantarget",
            value=targets,
        )

    def compose(self) -> ComposeResult:
        question = Static(
            Text("Would you like to create a terraform plan?", "bold"), id="question"
        )
        if self.var_file:
            self.input.value = self.var_file
        yield Grid(
            question,
            Horizontal(Static("Var-file:", id="varfilelabel"), self.input),
            self.checkbox,
            Button("Yes", variant="primary", id="yes"),
            Button("No", id="no"),
            id="tfvars",
        )
        self.input.focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "yes":
            self.dismiss((self.input.value, self.checkbox.value))
        else:
            self.dismiss(None)

    def on_key(self, event) -> None:
        if event.key == "y":
            self.dismiss((self.input.value, self.checkbox.value))
        elif event.key == "n" or event.key == "escape":
            self.dismiss(None)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.dismiss((self.input.value, self.checkbox.value))


class HelpModal(ModalScreen):
    help_message = (
        ("ENTER", "View resource details"),
        ("ESC", "Go back"),
        ("S / Space", "Select current resource (toggle)"),
        ("F", "Show resource/plan on full screen; Hold SHIFT/OPTIONS to copy text"),
        ("X", "Expose sensitive values in resource screen"),
        ("D", "Delete selected resources, or highlighted resource if none is selected"),
        ("T", "Taint selected resources, or highlighted resource if none is selected"),
        (
            "U",
            "Untaint selected resources, or highlighted resource if none is selected",
        ),
        ("C", "Copy selected resource's name or description to clipboard"),
        ("R", "Refresh state tree"),
        (
            "P",
            "Create execution plan, with an optional var-file and target list",
        ),
        (
            "Ctrl+D",
            "Create destruction plan, with an optional var-file and target list",
        ),
        ("A", "Apply current plan, available only if a valid plan was created"),
        ("/", "Filter tree based on text inside resources names and descriptions"),
        ("0-9", "Collapse the state tree to the selected level, 0 expands all nodes"),
        ("W", "Switch workspace"),
        ("M", "Toggle dark mode"),
        ("Q", "Quit"),
    )

    def compose(self) -> ComposeResult:
        button = Button("OK")
        table = DataTable(
            show_cursor=False,
            zebra_stripes=True,
        )
        table.add_columns(
            Text("Key", "bold", justify="center"),
            Text("Action", "bold", justify="center"),
        )
        for row in self.help_message:
            styled_row = [Text(str(row[0]), justify="center"), Text(row[1])]
            table.add_row(*styled_row)
        yield Grid(table, button, id="help")
        button.focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(None)

    def on_key(self, event) -> None:
        if event.key == "escape" or event.key == "enter":
            self.dismiss(None)
