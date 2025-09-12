# Runoff Model Builder (pyromb)
Author: Tom Norman

The Pyromb (PR) library builds both RORB[1], WBNM[2] and URBS model input files from ESRI shapefiles typically generated through a GIS package. This library's primary reason for existing is for use within the QGIS plugins [**Runoff Model Builder**](https://plugins.qgis.org/plugins/runoff_model/).

Using the plugin is in QGIS is straightforward, it takes four shapefiles that represent the catchment and outputs a control file to be used with either RORB, WBNM or URBS. The plugin is a processing plugin and will appear under "Runoff Model" within the Processing Toolbox. Complete use documentation is provided in the Pyromb library repositiory. 

 - To build a RORB control vector, select the **Build RORB** process.  
 - To build a WBNM runfile, select the **Build WBNM** process (Currently Unavailable).
 - To build a URBS control vector, select the **Build URBS** process.  

The library as it stands, is a minimal viable implementation of RORB, URBS and WBNM control files. It does however solve the primary issue with text file input models, that is, the need to manually transcribe information from GIS to the text file or graphical editor. Pyromb is now compatible with the RORB GE, therefore the generated control vector files can be easily modified for more complex catchments. 

MiRORB is a similar more advance tool which uses the GIS package MapInfo. The unavailability of MiRORB for QGIS inspired this project. This library is not however GIS package dependent. Pyromb is a stand alone python package able to be used directly by a python application if necessary. The QGIS plugins developed in conjunction with this project only feeds the shapefiles to this library for processing. As such this library can be used for any GIS software package. 

1. https://www.harc.com.au/software/rorb/
2. https://wbnm.com.au/
3. URBS = https://search.informit.org/doi/10.3316/informit.905985293458115
    Unified River Basin Simulator: A Rainfall Runoff Routing Model for Flood Forecasting & Design Version 6.65 by D. G. Carroll November 2023
    software and manual available from don.carroll@urbs.com.au

## Installing


### Dependencies
[Numpy](https://numpy.org/)
[Pandas](https://pandas.pydata.org/)
[Matplotlib](https://matplotlib.org/)

### Installing python package 

    $ pip install pyromb

### Installing for the QGIS Runoff Model Builder plugin:
For **MacOS or Linux**, QGIS does not have its own python environment so PR can be installed through pip directly from the terminal by using the command above.  

For **Windows**, QGIS has its own python environment. To install PR to work with QGIS, it needs to be installed via the OSGeo4W shell. 
Two methods depending on your version of QGIS, for newer versions,
1. Open the OSGeo4W Shell (may need admin permission)
2. Install via pip
###
    $ pip install pyromb

If that fails, try:
1. Open the OSGeo4W Shell (may need admin permission)
2. Enter **py3_env**
3. Install via pip
###
    $ python -m pip install pyromb

### Installing the QGIS Runoff Model Builder Plugin
1. Install v first
2. Open QGIS Plugin Manager, search for [**Runoff Model Builder**](https://plugins.qgis.org/plugins/runoff_model/) and install
3. Runoff Model Build is a processing plugin and is located in the processing toolbox under **Runoff Model**


## Setting Up A Catchment
PyRomb uses four shapefiles to provide the necessary information to build the RORB, URBS or WBNM vector, these are detailed below. The attributes that must be present in the shapefile so that PR has can build the control files. The easiest way to ensure the necessary attributes are present is to use the example shapefiles in the [data](https://github.com/norman-tom/pyromb/tree/main/data) folder. 

**WARNING**   
the id fields must be globally unique between the reaches, confluences and centroids otherwise the .catg / .vec file will not build correctly. This will be updated in subsequent releases. 

### Reaches
Reaches are the connection between basins and confluences.  

**Type**  
Line geometry.  
**Attributes**  
'id' - The name of the reach [string].  
's' - The slope of the reach (m/m) [double].  
't' - The reach type. [integer].  
**Support**  
Type 1 reach only.  
**Notes**  
Reach length is derived from the shapefile geometry. 

### Centroids
Centroids represent the basin attributes and are located as close to the basin centroid as possible, while still intersecting a reach.  

**Type**  
Point geometry  
**Attributes**  
'id' The name of the basin [string]  
'fi' The fraction impervious $\in[0,1]$ [decimal]  
**Support**  
Fraction impervious  
**Notes**  
Centroid to Basin matching is done through nearest neighbour. If a centroid is moved too far away from the basin’s true centroid, it may match with another basin, or not match at all. 
### Basins
Basins are only necessary to provide the centroid with an area. This was done to avoid having to transcribe area information into the Centroid shapefile as an attribute.  

**Type**  
Polygon geometry.  
**Attributes**  
None  
**Support**  
None  
**Notes**  
None
### Confluences
Confluences are the location where reaches meet, which isn't a centroid (no basin information associated).  

**Type**  
Point geometry  
**Attributes**  
'id' The name of the confluence [string]  
'out' Flag whether this confluence is the outfall [integer]  
<p>If no outlet is set, building the catchment will fail. If more than one is set, the first confluence with this attribute set will be adopted as the outlet. </p>

**Support**  
Confluence Only  
**Notes**  
In the future, these will represent other features like storage. 
### Example Catchment
![Catchment Overview](https://github.com/norman-tom/gisrom/blob/main/documentation/catchment_overview.png)

1. Basins are built in the preferred manner. There are various ways to produce the sub-catchments boundaries, please refer to your typical workflow to do so. These are nothing more than polygons that represent the boundaries of your subcatchments. 
2. Centroids are created from the basins, either using the in-built centroid tool in QGIS or estimating the location. Centroids represent a sub-area in the RORB Model. These don’t have the be at the centroid, these can be moved to suit the reaches. 
3. Confluences are manually located at junctions of reaches, these represent junction nodes in the RORB model and outlet locations in WBNM. 
4. Reach is the thalweg of the flow paths through the catchment. These are disjointed at each confluence and centroid, that is, they must start at an upstream confluence or centroid and end at the immediately downstream confluence or centroid.
5. Out location, the outlet of the catchment must be explicitly nominated by setting the GIS attribute as 1. All other confluence should have this attribute set to 0. 

An example of a built catchment can be found in the data folder. 

# Roadmap
Currently working on autogenerating the catchment diagram from an outlet location. That is, given an outlet location and DEM -> create subcatchment boundaries, reaches, centroids and confluences. The hope is that this will enable hydrographs to be generated very fast, with a high degree of scalability.    

___

___

# QUICKSTART Comparing URBS and RORB

**Author**: Lindsay Millard 21 Aug 2025 

**Purpose**: To provide notes and roadmap for implementation of URBS plugin to work with PyRomb in parallel to existing RORB.

## Conceptual Model and Traversal Logic
Both RORB and URBS use a sequential, depth-first traversal of the catchment network to build their instruction set.

**RORB**: Calls this sequence the "Control Vector". It's a list of numerical codes (1, 2, 3, 4, etc.) that dictate the order of operations. The data for each operation (like reach length) follows the code on the same line.

**URBS**: Uses a series of text-based commands (RAIN, ADD RAIN, STORE, etc.). The data for each command is provided as named parameters within the command line (e.g., L=4.7).
The core traversal logic implemented in PyRomb's Traveller is applicable to both. The primary difference is the function that writes the output string at each step of the traversal.

## The URBS Conceptual Model: "The Running Hydrograph"
Unlike RORB, which often defines the entire network structure first and then simulates, URBS builds its network sequentially.
Think of the .vec file as a series of instructions for a single "running hydrograph" that flows through the catchment.

1.  **Start a Flow:** You begin at a headwater subcatchment. The `RAIN` command takes the rainfall, applies it to this subcatchment (using properties from the `.cat` file), and generates the initial "running hydrograph". This command also routes that hydrograph down its associated reach.
2.  **Add to the Flow:** As you move downstream, you encounter another subcatchment. The `ADD RAIN` command calculates the runoff from this new subcatchment, adds it to the "running hydrograph," and routes the *combined* flow down the next reach.
3.  **Handle Tributaries (Junctions):** When the main channel meets a tributary, you need to pause the main flow.
    *   `STORE` temporarily saves the "running hydrograph" of the main channel.
    *   You then define the entire tributary from its headwaters down to the junction using a new set of `RAIN` and `ADD RAIN` commands.
    *   `GET` retrieves the saved main channel hydrograph and adds the now-complete tributary hydrograph to it. The "running hydrograph" is now the combined flow downstream of the junction.
4.  **Route without Local Inflow:** Sometimes you have a long river reach with no significant local inflow. The `ROUTE` command simply takes the current "running hydrograph" and routes it through this reach. The `ROUTE THRU #i` syntax is powerful here, as it tells URBS to use the physical characteristics (like slope or roughness) of subcatchment `#i` for this routing reach.
5.  **Define Output:** The `PRINT` command tells URBS, "At this point in the sequence, write the current state of the 'running hydrograph' to an output file." This is how you define an output node.

*   **Subcatchment Object:** Has properties like `Index`, `Name`, `Area`, `UrbanFraction`, etc. This data populates the `.cat` file.
*   **Reach Object (Link):** Connects two nodes. Has properties like `Length`, and is associated with one `Subcatchment Object` for its physical characteristics.
*   **Node Object (Junction):** A point where reaches connect. Can be designated as an "Output Point".

### 2. File Structure Comparison

This is a fundamental difference in philosophy that your GUI's "Save" function must handle.

| Feature | RORB (.catg) | URBS (.vec/.u & .cat) |
| :--- | :--- | :--- |
| **Primary File(s)** | A single, monolithic file containing the control vector, sub-area data, reach data, graphical data, and often the storm data. | Two primary files. The **`.vec` or `.u`** file contains the control sequence (commands). The **`.cat`** file contains the tabular sub-catchment data (Area, Imperviousness, etc.). |
| **Data Linkage** | All data is contained within the file. | The `.vec` file links to the `.cat` file via the sub-catchment index number (`RAIN #1` refers to Index 1 in the `.cat` file). |
| **GUI Implication** | "Save" writes one comprehensive file. | "Save" must write/update **two separate files** that are inter-dependent. |

### 3. Command / Control Code Equivalence

This is the core of the translation. The logic is nearly identical, but the syntax is different.

| Hydrologic Action | RORB Control Code | URBS Command | Notes |
| :--- | :--- | :--- | :--- |
| **Start a branch (Headwater)** | `Code 1` (Sub-area Inflow) | `RAIN #{index}` | Both commands initiate a "running hydrograph" from a headwater sub-catchment. |
| **Add inflow & route** | `Code 2` (Add in Sub-area Inflow & Route) | `ADD RAIN #{index}` | Both commands add runoff from a subcatchment to the existing "running hydrograph". |
| **Store hydrograph (at junction)** | `Code 3` (Store Hydrograph) | `STORE.` | The logic is identical: save the main channel flow, then process the tributary. |
| **Add stored hydrograph** | `Code 4` (Add in Stored Hydrograph) | `GET.` | The logic is identical: retrieve the main channel flow and add the tributary flow to it. |
| **Route without local inflow** | `Code 5` (Route Hydrograph) | `ROUTE THRU #{index}` | Both are used for pure routing reaches. URBS's `THRU` command is used to associate the reach with the physical properties of a specific sub-catchment from the `.cat` file. |
| **Print Output at a Node** | `Code 7` (Print Calculated) / `Code 7.1` (Print vs Gauged) | `PRINT. {location_name}` | Both define an output location. URBS requires a text-based location name. |
| **Special Storage** | `Code 6` (Existing Special Storage) | `DAM ROUTE ...` | Both are used to model reservoirs, dams, etc. The implementation details vary significantly. |
| **End of Model Definition** | `Code 0` (End of Control Vector) | `END OF CATCHMENT DATA.` | Both commands signify the end of the routing instructions. |

### 4. Parameter and Data Input Comparison

| Data Type | RORB | URBS |
| :--- | :--- | :--- |
| **Sub-catchment Properties** (Area, Imperviousness) | Entered directly in the `.catg` file within a dedicated "sub-area data" block (Item 6.x). | Entered in a separate **`.cat` CSV file**. Your GUI will need a dedicated table editor for this. |
| **Reach Properties** (Length, Type/Slope) | Entered on the same line as the control code (e.g., `1, 1, 4.7, -99`). | Entered as named parameters within the command (e.g., `L=4.7 Sc=0.01`). |
| **Global Parameters** (kc, m, IL) | Entered interactively via the program's GUI windows. | Entered in the `.vec` file using the `DEFAULT PARAMETERS` command, or set via environment variables. |

### 5. Units Comparison


| Parameter | RORB Unit (Table 5-1) | URBS Unit (Table 2) | Notes |
| :--- | :--- | :--- | :--- |
| Reach Length | `km` | `km` | Identical. |
| Sub-catchment Area | `km²` | `km²` | Identical. |
| Discharge | `m³/s` | `m³/s` | Identical. |
| Rainfall | `mm` | `mm` | Identical. |
| Initial / Continuing Loss | `mm` / `mm/h` | `mm` / `mm/h` | Identical. |
| **Channel / Reach Slope** | **`%`** | **`m/m`** | **CRITICAL DIFFERENCE!** Your GUI must handle this conversion. |
| Fraction Imperviousness | Fraction (0-1) | Fraction (0-1) | Identical. |


## END NOTES:
The URBS model has been under development over the past 25 years. Its technical basis is in the
pioneering work carried out by Laurenson & Mein and later as WT42 developed by the Queensland
Department of Natural Resources and Mines. The primary focus of its development has been flood
forecasting and design flood hydrology. Central to its development is the philosophy that the model is
a tool that can be readily employed by flood forecasting practitioners and design flood hydrologists

Aitken A.P. (1975a) Hydrologic Investigation and Design of Urban Stormwater Drainage
Systems., Aust. Water Resources Council Tech. Paper No. 10, Dept of the Environment and
Conservation, A.G.P.S., Canberra.
Aitken A.P. (1975b) Catchment Models for Urban Areas, included in Prediction in Catchment
Hydrology, Australia Academy of Science.
Carroll, D.G. (1991) Flood Warning and Monitoring in the Brisbane City Area Using Event Based
Radio Telemetry Systems, MEngSc Thesis, QUT, Queensland.
Carroll D.G. & Collins N.I., (1993), Integrated Hydrologic and Hydraulic Modelling, WaterComp
Conference Proceedings, Institution of Engineers.
Carroll D.G. (1994), Aspects of the URBS Runoff Routing model, IE Aust Conf: Water Down
Under, Adelaide, Nov. 1994.
Carroll D.G. (1995), Assessment of the Effects of Urbanisation, Proceedings, 2nd Intl Stormwater
Management Conference, IE Aust, Melbourne July 1995.
Carroll D.G. (2008) Enhanced Rainfall Event Generation for Monte Carlo Simulation Technique
of Design Flood Estimation. IE Aust Conf: Water Down Under, Adelaide, Apr 2008.