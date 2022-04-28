Set `images_folder` to the full path of the folder containing your images. 
The folder should have at least one image for the light mode,
and at least one for the dark mode.

Folders will be separated either by forward slashes, 
or by double backwards slashes, for example:

* `/home/user/anki-wallpapers`
* `C:\\Users\\user\\anki-wallpapers\\`

Dark mode images will have `dark` in their name, 
separated from other parts of the name using the characters `-`, `_`, `.` or space.

By default, images will be anchored by the centre, 
that is, the center of the image will be in the center of the window.
You can change anchoring by putting any of the following in the file name: 
`center`, `top`, `left`, `bottom`, `right`.

Some examples:

* `clouds.jpg`: light mode, center-anchored
* `gloomy_mountains-dark-top.jpeg`: dark mode, top-anchored.

The configuration takes effect on restart.