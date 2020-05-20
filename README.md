# ItalicExtremes

Glyphs App Filter plugin to add points on a specified angle.

![Italic Extremes](ItalicExtremes.png "Italic Extremes")

### How to use

As all filters, the plugin can be used on an opened glyph or on a selection of glyphs in the Font panel. If nodes or segments are selected in an opened glyph, only the selection will be affected.

The default angle is the italic angle from the selected master when launching the plugin.
Multiple angles can be entered separated by commas, and will be processed successively.

The checkboxes allow to optionally delete V/H extremes or slanted curve nodes that match the specified angles, effectively switching an outline between V/H and Italic extremes.

### Apply on export

You can apply *Italic Extremes* on export by adding it as a custom parameter to an instance. You can copy a parameter from the bottom left button of the plugin's window (it would then have the currently set options), or add the custom parameter yourself:
1. Add a new *Filter* custom parameter
2. Add *ItalicExtremes;* in its value.
3. Add desired parameters, always separated by semicolons. The available parameters are: 
  -*angles*: a comma-separated list of angles to add nodes on
  -*option*: either *AddI* to add slanted nodes or *AddHV* to add horizontal/vertical extremes
  -*removeV*: *0* or *1* to enable/disable suppression of vertical extremes if option is set to "AddI"
  -*removeH*: *0* or *1* to enable/disable suppression of horizontal extremes if option is set to "AddI"
  -*removeI*: *0* or *1* to enable/disable suppression of curve nodes that match *angles* if option is set to "AddHV"

Custom Parameter example: *Filter = "ItalicExtremes; angles:16; option:AddI; removeV:1; removeH:0; removeI:0";*

### Note

Keep in mind that not all curves can be replicated exactly with a different point placement. Glyphs' algorythm to keep a shape when removing nodes works well, but is not magic.

Especially if you use the plugin as an Instance filter, do it if you understand the implications of removing certain points for your particular outlines. The main purpose for the use on export would be to add vertical extremes on outlines built with slanted nodes in the source file.

It is recommended that you keep a copy of the original outline somewhere before using the plugin, either in background or a backup layer.

### License

Copyright 2020 Joachim Vu.

Based on the Glyphs plugin SDK sample code by Georg Seifert (@schriftgestalt).

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

See the License file included in this repository for further details.