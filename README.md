This is a tool for streamers to help display information about your wonders, policies, and religion in Civ 5.
You can get the latest version at https://github.com/Hyphen-ated/civ5tracker/releases (click to download the latest
zip file that does not have "source code" in the name)

It must be used in conjunction with the "Export Info" mod, available at
https://github.com/Hyphen-ated/civ5exportinfo

Start a game with the mod active at least once before you run this program.

It puts info in the text files in its "output files/" folder, and it also creates a miniature webpage that you can
overlay onto your stream using the "CLR Browser" plugin.
To do so, first go install that plugin here: https://obsproject.com/forum/resources/clr-browser-source-plugin.22/
Then, add a CLR capture and set the following things:
 * URL to "http://localhost:8085/sidebar.html"
 * Width to 254
 * Height to whatever you want (too short and it might run out of room)
It should look something like this: http://i.imgur.com/csmV3QL.png

You can edit the template.html file if you want to tweak the appearance.
You can also do a bunch of text overlays with the text files, but that's very fiddly.