# 📚 Neon Dashboard Readme 📚

Neon Dashboard is a web-based visualization tool for exploring and analyzing neon data. It was created as part of the research project outlined in the paper (** add link).

There are many ways to run this application on your local machine:

## 🚀 Easiest Method: How to Clone Docker Image and Start the Bokeh Application from Docker Hub 📦

To quickly get started with the Neon Dashboard Bokeh application, you can use the easiest method by pulling the pre-built Docker image from Docker Hub. 📦

Open a terminal or command prompt and run the following command to pull the image:

```bash
docker pull negin513/neon-app
```

Once the image is pulled successfully, run the Bokeh application in a Docker container with the following command. This will forward the port `8080`, making the application publicly available: 🚀

```bash
docker run -p 8080:5006 negin513/neon-app
```

The Bokeh application should now be up and running inside the Docker container. You can access it in your web browser at http://localhost:8080. 🎉🎉🎉


## 🚀 How to Run with Container? 🚀

To run Neon Dashboard using Docker container, follow these steps:

1. Make sure you have Docker installed on your system.

2. Clone or download the Neon Dashboard repository from https://github.com/negin513/neon_dashboard.
    ```
    git clone https://github.com/negin513/neon_dashboard
    ```

3. Navigate to the root directory of the cloned/downloaded repository.
    ```
    cd neon_dashboard
    ```

4. Build the Docker image using the provided Dockerfile:
   ```
   docker build -t neon-app .
   ```

5. Once the image is built, run the container with port mapping:

   ```
   docker run -p 5006:5006 neon-app
   ```

6. The Neon Dashboard should now be accessible in your web browser at `http://localhost:5006`.

Sure! Here's an additional section on how to run Neon Dashboard without using a Docker container, using Conda for managing the Python environment.

## 🏃 How to Run with Conda (Without Docker Container)? 🏃

To run Neon Dashboard without using a Docker container, you'll need to have Conda and Python installed on your system. Follow these steps:

1. lone or download the Neon Dashboard repository from https://github.com/negin513/neon_dashboard.
    ```
    git clone https://github.com/negin513/neon_dashboard
    ```

2. Create a Conda environment and install the required Python packages:
   ```
   conda create -n neon-env python=3.9.6
   conda activate neon-env
   pip install -r requirements.txt
   ```

   The first command creates a new Conda environment named "neon-env". The second command activates the environment. The third command installs Bokeh and its required dependencies, while the fourth command installs any additional Python packages listed in the requirements.txt file.

3. Once the dependencies are installed, navigate to the root directory of the Neon Dashboard repository and activate the `ncar-env` environment:
```
   conda activate neon-env
   cd neon_dashboard
```

4. Run the Bokeh application:
   ```
   bokeh serve --allow-websocket-origin=localhost:5006 neon_dashboard
   ```

   The `--allow-websocket-origin` flag is used to enable connections from the local host.

5. The Neon Dashboard should now be accessible in your web browser at `http://localhost:5006`.



## 📄 Citing the Paper 📄

If you use Neon Dashboard in your research or work and want to cite the original paper, please use the following citation format [***].

🎉🎉🎉 Have fun exploring your neon data with Neon Dashboard! 🎉🎉🎉