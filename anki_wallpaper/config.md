Set `folder_with_wallpapers` to the full path of the folder 
containing your wallpaper images. 
The folder should have at least one wallpaper for the light mode,
and at least one for the dark mode.

Folders will be separated either by forward slashes, 
or by double backwards slashes, for example:

* `/home/user/anki-wallpapers`
* `C:\\Users\\user\\anki-wallpapers\\`

Dark mode wallpapers will have `dark` in their name, 
separated from other parts of the name using the characters `-`, `_`, `.` or space.

By default, wallpapers will be anchored by the centre, 
that is, the center of the wallpaper will be in the center of the window.
You can change anchoring by putting any of the following in the file name: 
`center`, `top`, `left`, `bottom`, `right`.

Some examples:

* `clouds.jpg`: light mode, center-anchored,
* `gloomy_mountains-dark-top.jpeg`: dark mode, top-anchored.

If `change_wallpaper_on_deck_browser` is `true`, 
the next wallpaper will be shown whenever you click on `Decks`
or press the `d` key. To disable, set to `false`.

The configuration takes effect on restart.