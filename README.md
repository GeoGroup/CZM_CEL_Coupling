Sure! Here's the English version of the `README.md`:

---

# README

## Overview

This script processes an Abaqus input file (`.inp`) and automatically inserts 3D cohesive elements (e.g., `COH3D8`, `COH3D6`) between specified elements to simulate fractures or sliding interfaces.

## Features

* Reads the original `.inp` file and parses nodes, elements, and Elsets.
* Duplicates nodes for each element to allow inter-element separation.
* Automatically detects shared faces between adjacent elements (based on node combinations).
* Differentiates between internal and boundary cohesive zones using a specified Elset (e.g., `slide`).
* Inserts cohesive elements (COH3D6 or COH3D8) between adjacent faces.
* Maintains node mapping and "stitches" non-cohesive regions to avoid duplicated nodes.
* Outputs a new `.inp` file (e.g., `slide-1.inp`) that includes the updated nodes, elements, and cohesive element Elsets (`cohin`, `cohout`).

## Usage

1. Place the original Abaqus input file in the same directory as the script and name it `slide.inp`.
2. Run the script.
3. After execution, a new Abaqus input file `slide-1.inp` will be generated for further analysis.

## Notes

* The `slide` Elset in the original file should define the region where cohesive elements are to be inserted.
* The script currently supports element types: `C3D4`, `C3D5`, `C3D6`, and `C3D8`.
* The cohesive element type is automatically determined based on the number of nodes per face.
* All cohesive elements are grouped into two Elsets: `cohin` (internal interfaces) and `cohout` (boundary interfaces).

---

This script can be extended further to support additional element types (e.g., 2D elements), material sections, or user-defined interface criteria.
