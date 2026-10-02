# Animaniacs: The Great Edgar Hunt Importer
A Blender add-on for importing models from Animaniacs: The Great Edgar Hunt. Currently, only the Xbox release is supported.

## Usage
1. Extract the .HOG files in the *resource* folder using this QuickBMS script: https://aluigi.altervista.org/bms/wart3_hps.bms. If the site is down, use a snapshot of the link from https://archive.org.
2. Download the latest version of this add-on from the [releases](https://github.com/jmancoder/animaniacs-tgeh-importer/releases) page and install it. Blender 4.2 and newer is supported.
3. In Blender, click *File->Import->Animaniacs BMSH/BSKL (.bmsh/.bskl)*.
4. Select both the BSKL and BMSH files of the model(s) you wish to import.
5. Click *Import BMSH/BSKL*.

## File formats
- BANB - Animation data
- BMSH - Geometry and material data (supported)
- BSKL - Bone data (supported)
- BTGA - Texture data
- BWAV - Sound effects
- LVL - Level data
- MDL - Text description of exported Maya scenes
- MRK - Unknown; appears to always be empty
- SUB - Cutscene subtitles
- TNF - Fonts
- XST - Music
