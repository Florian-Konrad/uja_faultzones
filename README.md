<h1 align="center">
  Upper Jurassic Aquifer Fault Zones (uja_faultzones)
  <br>
  <br>
  a parametric investigation tool for fault zones and their effect on well productivity
  <br>
</h1>

<h4 align="center">Reduced Basis Model for a single inclined fault zone pierced by a vertical well inside of a porous aquifer - trained on parameter ranges for the Upper Jurassic aquifer of the Northern Alpine Foreland Basin in Southern Germany - based on its typical aquifer geometry</h4>

<p align="center">
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/license-GPLv3-blue.svg"
         alt="GitHub License">
  </a>
</p>



## About

This Python tool is based on a numerical FE model of a typical fault zone for the Upper Jurassic aquifer in Southern Germany (https://doi.org/10.1186/s40517-019-0137-4). By applying the Reduced Basis method (https://doi.org/10.1007/s10596-019-09916-6, https://github.com/denise91/DwarfElephant) a reduced model was generated which can be used now to calculate the pressure curves of pumping tests of a vertical well inside a 70° inclined fault zone surrounded by an porous aquifer of 500 meter thickness by only supplying the governing hydraulic parameters in a table as `.csv` file. Calculation times for one parameter combination are generally below 1 second (~0.4s per simulation) depending on the computer system.

Focus of uja_faultzones is to simulate two pumping tests (500h water extraction) for each parameter combination (in the range of the Upper Jurassic Aquifer) that it is given, one with and one without the fault zone. It then evaluates the pressure evolution inside the well through the Bourdet Derivative (DER) to derive the main flow regime. Next, it compares the two pressure curves in an attempt to calculate the wells relative productivity index improvement through the fault zone. This calculation is only possible if the difference between the two pressure curves becomes numerically stable which depends on the chosen parameters (less than 0.005% value change per hour). Pressure curves can be ouput as .csv files as well as plots in various formats.

<p align="center">
    <a href="https://github.com/Florian-Konrad/uja_faultzones/"><img src="images/fault_zone_concept.png" alt="fault_zone_concept" width="600"></a>
</p>

## Licence
uja_faultzones is distributed under the [GNU GENERAL PUBLIC LICENSE v3](https://github.com/Florian-Konrad/uja_faultzones/master/LICENSE).


## Getting Started

#### Minimum System Requirements
* Python 3+
* Git
* Disk: 2 GBs

#### Installation

* Install git (https://github.com/git-guides/install-git)

* Clone uja_faultzones:

    ```
    cd ~/
    git clone https://github.com/Florian-Konrad/uja_faultzones.git
    cd ~/uja_faultzones
    git checkout master
    ```
* Download and insert Reduced Basis Models into ~/uja_faultzones/fzpicalc/

    The folder containing the reduced basis models can be obtained here: https://mediatum.ub.tum.de/1579932

    The final folder path should then be `~/uja_faultzones/fzpicalc/RB_Modelz_v4`

* Install Miniconda3 e.g. Linux Users:

    https://conda.io/projects/conda/en/latest/user-guide/install/index.html

    ```
    curl -L -O https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
    bash Miniconda3-latest-Linux-x86_64.sh -b -p ~/miniconda3
    export PATH=$HOME/miniconda3/bin:$PATH
    ```

* Install Python and Packages:

    ```
    conda env create -n uja_faultzones -f uja_pythonenv.yml
    conda activate uja_faultzones
    ```


## Usage

To use uja_faultzones you need to provide an `.csv` input file containing sets of parameter combinations.
Have a look at `test_input_set.csv` on how to set it up.

IMPORTANT: hydraulic fault zone properties have to be higher than matrix for valid results regarding the fault zone associated well PI increase; if the user is only interested in the pressure curves and plots they are still valid in that case!

Column names must contain (exact spelling): `k_matrix`, `k_fault`, `viscosity`, `S_matrix`, `S_fault`, `rate`, `fz_thickness`

The parameter values must be provided in the following units:
* `k_matrix` = matrix permeability [m²] (valid range: 1.0e-17 - 2.0e-11)
* `k_fault` = fault zone permeability [m²] (valid range: 1.0e-14 - 1.0e-9)
* `viscosity` = fluid viscosity [Pa*s] (valid range: 1.0e-4 - 3.0e-4)
* `S_matrix` = specific matrix storage [1/Pa] (valid range: 2.0e-12 - 1.6e-10)
* `S_fault` = specific fault zone storage [1/Pa] (valid range: 2.0e-12 - 1.6e-10)
* `rate` = production rate applied to well [l/s] (fix to 20, 10 - 20 possible)
* `fz_thickness` = fault zone thickness [m] (valid discrete values: 10, 15, 20, 35, 50, 75, 100, 200, 300)

Put the `.csv` input file into the same folder as `uja_faultzones.py`.
Open `uja_faultzones.py` and provide the `.csv` input file name under USER INPUT.

If you want to output Plots of the derivative analysis as well as the PI alteration calculation for each individual parameter combination set `plotting = True`

If you want to save the pressure information as `.csv` files for each individual parameter combination set `save_pressure_curves = True`

Make sure the `uja_faultzones` python environment is activated.

Run it:

  ```
  cd ~/uja_faultzones
  python uja_faultzones.py
  ```

Based on the current time stamp a new folder is created which will contain all requested output as well as a summary `.csv` file containing the main results for all parameter combinations provided in the input `.csv` file. Its name is `calculated_*yourinputfilename*.csv`.


Results:

* `main flow type - matrix` / `main flow type - fault zone` = result of derivative analysis (radial, bilinear, linear, steep or unspecifiable_hydr_changes)
    * radial, bilinear, linear = standard well test analysis nomenclature
    * steep = the fault zone experiences a negative boundary like steep Bourdet Derivative (DER) when the pressure transient moves into the matrix
    * unspecifiable_hydr_changes = the Bourdet Derivative (DER) does not evolve into a specific classifiable flow regime, just slight positive or negative slope are experienced that don't allow for a classification
* `Pi_ref Matrix [l/s/MPa]` = reference productivity index of the matrix scenario which is used to calculate the relative fault zone influence (Rel. fault zone PI influence [-])
* `P_ref pick time [h]` = time at which the reference PI is picked (342.76 means Pi_ref was derived through radial DER extrapolation to guarantee trend-free comparison)
* `Rel. fault zone PI influence [-]` = main result of fault zone analysis, relative increase of the wells PI through fault zone presence, IMPORTANT: will be empty if no equilibrium was found
* `Pi change FZ [l/s/MPa]` = absolute increase of the wells PI through fault zone presence
* `dP change FZ [MPa]` = pressure difference between matrix and fault zone pressure curve when equilibrium (less than 0.005% value change per hour) is reached
* `Pi change pick time [h]` = time at which the equilibrium was found



Generating an input `.csv` file by grid sampling:

Open `generate_input_grid.py` and edit the section under USER INPUT.

Have a look at the comments to get an idea of how to define the USER INPUT

Run the file:

  ```
  cd ~/uja_faultzones
  python generate_input_grid.py
  ```


## Cite
