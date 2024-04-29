# 📚 NCAR-NEON Dashboard Readme 📚

[![DOI](https://zenodo.org/badge/558070250.svg)](https://zenodo.org/doi/10.5281/zenodo.10956996)
[![Neon Dashboard](https://img.shields.io/badge/Neon_Dashboard-Click_Here-green.svg)](https://ncar.nationalsciencedatafabric.org/neon-demo/v1/)


**To access the NEON Dashboard, please visit the following link: [Neon Dashboard](https://ncar.nationalsciencedatafabric.org/neon-demo/v1/).**

The NCAR-NEON Dashboard provides an interactive visualization interface for visualizing and analyzing data collected by the [National Ecological Observatory Network (NEON)](https://www.neonscience.org/) and comparing it with with the Community Terrestrial System Model (CTSM) simulations at those points. It was created as part of the research project outlined in [this paper](https://gmd.copernicus.org/articles/16/5979/2023/gmd-16-5979-2023.pdf).

This dashboard enables users from anywhere in the world to explore and interact with model outputs and observations on the fly without any requirements for advanced computational resources.  This tool allows users to generate graphs and statistical summaries comparing CTSM simulations and observational data for NEON sites without downloading the observational data or running the model. Users access a Graphical User Interface (GUI) to select individual NEON sites, variables, and output frequencies to visualize. The tool offers different types of interactive visualizations and statistical summaries based on user selections. This interactive visualization dashboard does not require specialist knowledge to operate; therefore, it can be used for educational outreach activities and in classrooms. Moreover, users
can interact with the dashboard using a browser, so it is possible to interact with the plots via a tablet or smartphone.

Users can customize the plots by selecting different data sources, time periods, and geographic regions. This dashboard is currently hosted on [the National Science Data Fabric (NSDF)](https://nationalsciencedatafabric.org/) and is publicly accessible to anyone to use!

Besides using the above link to access the NEON Dashboard, you can also run the application on your local machine. This README provides instructions on how to run the NEON Dashboard application using or without a Docker container.

--------------------------------------------------
## How to Cite this Dashboard? 

If you use NEON Dashboard in your research or work and want to cite the original paper, please use this DOI for citing this dashboard:  [![DOI](https://zenodo.org/badge/558070250.svg)](https://zenodo.org/doi/10.5281/zenodo.10956996)


--------------------------------------------------

## How to run the NEON Dashboard application yourself?

Besides interacting with neon dashboard at [Neon Dashboard](https://ncar.nationalsciencedatafabric.org/neon-demo/v1/), you can run it locally on your machine!

There are many ways to run this application on your local machine:

### 🚀 Easiest Method: Using Docker Image Directly!

To get started with the NEON Dashboard Bokeh application, you can use the easiest method by pulling the pre-built Docker image from Docker Hub. 📦

Open a terminal or command prompt and run the following command to pull the image:

```bash
docker pull negin513/neon-app_latest
```

Once the image is pulled successfully, run the Bokeh application in a Docker container with the following command. This will forward the port `8080`, making the application publicly available: 🚀

```bash
docker run -p 8080:5006 negin513/neon-app_latest
```

The Bokeh application should now be up and running inside the Docker container. You can access it in your web browser at http://localhost:8080. 🎉🎉🎉

### How to Run this Application without Docker Container? (using Conda) 🏃

To run NEON Dashboard without using a Docker container, you'll need to have Conda and Python installed on your system. Follow these steps:

1. lone or download the NEON Dashboard repository from https://github.com/negin513/NEON_dashboard.
    ```
    git clone https://github.com/negin513/NEON_dashboard
    ```

2. Create a Conda environment and install the required Python packages:
   ```
   conda create -n neon-env python=3.9.6
   conda activate neon-env
   pip install -r requirements.txt
   ```

   The first command creates a new Conda environment named "neon-env". The second command activates the environment. The third command installs Bokeh and its required dependencies, while the fourth command installs any additional Python packages listed in the requirements.txt file.

3. Once the dependencies are installed, navigate to the root directory of the NEON Dashboard repository and activate the `ncar-env` environment:
```
   conda activate neon-env
   cd neon_dashboard
```

4. Run the Bokeh application:
   ```
   bokeh serve --allow-websocket-origin=localhost:5006 neon_dashboard
   ```

   The `--allow-websocket-origin` flag is used to enable connections from the local host.

5. The NEON Dashboard should now be accessible in your web browser at `http://localhost:5006`.

## 📄 Citing the Paper 📄

If you use NEON Dashboard in your research or work and want to cite the original paper, please use the following citation:

🎉🎉🎉 Have fun exploring your NEON data with NEON Dashboard! 🎉🎉🎉
