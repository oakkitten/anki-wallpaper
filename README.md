## Wallpaper — an Anki add-on

Set and change the background image of Anki’s main window, Add cards dialog,
Edit current card dialog, and Card previewer on the fly.

<p align="center">
  <img alt="Screenshots" src="https://user-images.githubusercontent.com/1710718/169703704-e21af84e-b67e-46fb-86b6-ca5ade7315ac.png">
  <i>
    Illustrations by
    <a href="https://www.pexels.com/photo/snow-capped-mountain-under-cloudy-sky-3389536/">
      Eberhard Grossgasteiger</a>,
    <a href="https://www.pexels.com/photo/empty-brown-canvas-235985/">
      Pixabay</a>,
    <a href="https://www.pexels.com/photo/white-and-black-mountain-wallpaper-933054/">
      Joyston Judah</a>
  </i>
</p>

This add-on was inspired by the awesome add-on 
[Custom Background and Gear Icon](https://github.com/AnKingMed/Custom-background-image-and-gear-icon). 
However, it takes a different approach to the way the background images are set. 
Among the advantages are:
* The wallpaper is set for the entire window, including the menu;
* The wallpaper is continuous—there’s only one per window;
* The wallpaper doesn’t flicker when navigating between decks;
* Dialogs can have wallpapers as well.

There are also some disadvantages due to platform limitations:
* You can’t resize the wallpaper along with the window;
* It is not possible to control wallpaper opacity as easily.

You will find configuration in _Tools_ → _Add-ons_ → _Config_, along with a short manual.
After configuring the folder with your wallpapers, 
you’ll be able to change the wallpaper via _View_ → _Next wallpaper_ 
(on Anki 2.1.49 _Tools_ → _Next wallpaper_),
as well as via the global shortcut <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>W</kbd>.
You will have to manually resize the wallpapers to your preferred size,
and if you need to change to opacity, you will also have to do it by hand. 
Sorry about that.

Note that by default Anki cards set their own background color in CSS.
In order to see the wallpaper while reviewing, you must remove the card background.
You can do so by going to _Browse_ → _Cards…_ → _Styling_ 
and removing the line with `background` or `background-color`.