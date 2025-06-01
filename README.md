# VoronoiCity

When I was looking at the Voronoi noise with rounded edges, I felt like I could create a city using the white edges as roads. 3D shapes were stacked and rotated to look like buildings and placed within the Voronoi regions with the image of Tokyo. Noise, 3D shapes, and skybox were all created procedurally.
See below.   
   
https://github.com/taKana671/NoiseTexture   
https://github.com/taKana671/shapes   
https://github.com/taKana671/skybox   
   
Mouse drag to rotate the entire city.

![Image](https://github.com/user-attachments/assets/f6f41979-a581-4e1f-a866-87b4665e9789)

# Requirements
* Panda3D 1.10.15
* numpy 2.2.4
  
# Environment
* Python 3.12
* Windows11

# Usage

#### Clone this repository with submodule.
```
git clone --recursive https://github.com/taKana671/VoronoiCity.git
```

#### Execute the following command
```
python voronoi_city.py
```

https://github.com/user-attachments/assets/161ab37a-eeb4-4208-9c7b-bc80149b089c

#### Key control

<table>
    <tr>
      <th>key</th>
      <th>description</th>
    </tr>
    <tr>
      <th>Esc</th>
      <th align="left">Close the screen.</th>
    </tr>
    <tr>
      <th>t</th>
      <th align="left">Toggles physical object display on and off.</th>
    </tr>
    <tr>
      <th>i</th>
      <th align="left">Click on a building and press the [i] key, its position and angle will be displayed on the console.</th>
    </tr>
    <tr>
      <th>r</th>
      <th align="left">Releases the building selected by pressing the i key.</th>
    </tr>
    <tr>
      <th>w</th>
      <th align="left">Toggles wireframe display on and off.</th>
    </tr>
    <tr>
      <th>v</th>
      <th align="left">Switch between sky view mode and moving view mode.</th>
    </tr>
</table>

In `skyview mode`, you can view the city from above and rotate the entire city by dragging the mouse. 
`moving view mode` allows you to move around the city by keystrokes below.
<table>
    <tr>
      <th>key</th>
      <th>description</th>
    </tr>
    <tr align="left">
      <th>up arrow</th>
      <th>Move forward.</th>
    </tr>
    <tr align="left">
      <th>left arrow</th>
      <th>Turn left.</th>
    </tr>
    <tr align="left">
      <th>right arrow</th>
      <th>Turn right.</th>
    </tr>
    <tr align="left">
      <th>down arrow</th>
      <th>Move backward.</th>
    </tr>
    <tr align="left">
      <th>u</th>
      <th>Go up.</th>
    </tr>
    <tr align="left">
      <th>d</th>
      <th>Go down.</th>
    </tr>
</table>

