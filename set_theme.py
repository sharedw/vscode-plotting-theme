import os
import json
import re
import matplotlib.pyplot as plt
import seaborn as sns


class JSONWithCommentsDecoder(json.JSONDecoder):
    """JSON decoder that automatically deals with the comments in vscode json esque settings"""

    def __init__(self, **kw):
        super().__init__(**kw)

    def decode(self, s: str):
        s = "\n".join(l for l in s.split("\n") if not l.lstrip(" ").startswith("//"))
        s = re.sub(r",\s*}", "}", s)  # Remove trailing commas
        s = re.sub(r",\s*]", "]", s)  # Remove trailing commas in arrays
        return super().decode(s)


def get_theme_name():
    """gets the active theme name from user's settings"""
    global_settings_path = os.path.expanduser(
        r"~\AppData\Roaming\Code\User\settings.json"
    )

    with open(global_settings_path, "r") as file:
        json_settings = json.load(file, cls=JSONWithCommentsDecoder)

    theme_name = json_settings.get("workbench.colorTheme", None)
    if not theme_name:
        return json_settings, "dark_modern"
    return json_settings, theme_name

json_settings, theme_name = get_theme_name()
print(theme_name)


def get_extension_filepath(theme_name):
    extension_folder_path = os.path.expanduser(r"~/.vscode/extensions/")
    default_folder = os.path.expanduser(
        r"~/AppData\Local\Programs\Microsoft VS Code\resources\app\extensions"
    )
    for location in [extension_folder_path, default_folder]:
        for folder_name in os.listdir(location):
            folder_path = os.path.join(location, folder_name)

            # Check if it is a directory
            if os.path.isdir(folder_path):
                # Path to the package.json file
                package_json_path = os.path.join(folder_path, "package.json")

                # Check if package.json exists in the folder
                if os.path.exists(package_json_path):
                    try:
                        # Open and load the package.json
                        with open(package_json_path, "r", encoding="utf-8") as f:
                            package_data = json.load(f, cls=JSONWithCommentsDecoder)

                        # Get the displayName from the package.json
                        contributes = package_data.get("contributes", {})
                        themes = contributes.get("themes", [])
                        name = package_data.get("name", '')
                        name = package_data.get('id', name)
                        name = name.replace('-', ' ')
                        category = package_data.get("categories", None)
                        if theme_name.lower() in name.lower() and category == [
                            "Themes"
                        ]:
                            theme_path = package_data["contributes"]["themes"][0].get(
                                "path", ""
                            )
                            #print(
                            #    f"Found theme: {name} in folder: {folder_path+theme_path}"
                            #)
                            return folder_path + theme_path
                        for theme in themes:
                            label = theme.get("label", "!!!")
                            if (
                                theme_name.lower() in label.lower()
                            ):  # Case-insensitive comparison
                                theme_path = theme.get("path", "")
                                #print(
                                #    f"Found theme: {label} in folder: {folder_path+theme_path}"
                                #)
                                return folder_path + theme_path
                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON in {package_json_path}: {e}")

    raise KeyError("Theme extension folder was not found")


if theme_name != "dark_modern":
    extension_path = get_extension_filepath(theme_name)
    with open(extension_path) as file:
        theme_settings = json.load(file, cls=JSONWithCommentsDecoder)
else:
    extension_path = os.path.expanduser(
        r"~/AppData\Local\Programs\Microsoft VS Code\resources\app\extensions\theme-defaults\themes\dark_modern.json"
    )
print(extension_path)
with open(extension_path) as file:
    theme_settings = json.load(file, cls=JSONWithCommentsDecoder)

if "workbench.colorCustomizations" in json_settings.keys():
    if f'[{theme_name}]' in json_settings["workbench.colorCustomizations"].keys():
        theme_settings['colors'].update(json_settings["workbench.colorCustomizations"][f'[{theme_name}]'])



def get_token_color(settings, token):
    try:
        return settings["semanticTokenColors"][token]
    except KeyError:
        pass
    for t in settings["tokenColors"]:
        if token in t.get("scope", []):
            return t["settings"]["foreground"]


bg_color = theme_settings["colors"].get("notebook.outputContainerBackgroundColor", None)
if not bg_color:
    #print('editor_bg color used')
    bg_color = theme_settings["colors"].get("editor.background", "#1E1E1E")

text_color = theme_settings["colors"].get("editor.foreground", "#FFFFFF")
string_color = get_token_color(theme_settings, "string")
function_color = get_token_color(theme_settings, "keyword")
comment_color = get_token_color(theme_settings, "comment")

#print(bg_color, text_color, string_color, comment_color, function_color)

custom_style = {
    "axes.facecolor": bg_color,
    "figure.facecolor": bg_color,
    "text.color": function_color,
    "axes.labelcolor": string_color,
    "xtick.color": text_color,
    "ytick.color": text_color,
    "axes.titlecolor": text_color,
    "grid.color": comment_color,
    "axes.edgecolor": text_color,
    "lines.markeredgecolor": bg_color
}

sns.set_style("darkgrid", rc=custom_style)

