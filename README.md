# Enabling Real-world Medical Compute Workflows on the Cloud (and others) to aid in Clinical Decision Making

# Current Code is in: main
## Team Members:
* Efe Sencan (esencan@bu.edu)
* Haoxuan(Harry) Li (harryli@bu.edu)
* Ronnakorn Rattanakornphan (ronrat@bu.edu)
* Yanni Pang (yanni@bu.edu)
## Team Mentors:
* Rudolph Pienaar (rudolph.pienaar@childrens.harvard.edu)
* Sandip Samal (sandip.samal@childrens.harvard.edu)
* Gideon Pinto (gideon.pinto@childrens.harvard.edu)
* Jennings Zhang (jennings.zhang@childrens.harvard.edu) 

## What is ChRIS project?

ChRIS (ChRIS Research Integration Service) ([ChRIS](http://chrisproject.org/)) is an active open source distributed data and computation framework, developed from inception as a platform to facilitate the execution of complex (research-focused) compute operations by nontechnical users. Its genesis arose from a realization that considerable programs of value exist in the research world and the observation that most (if not all) of these programs are rarely used by anyone other than the original authors. ChRIS, at its heart, is a platform that attempts to cross this divide. It has grown into a container-based scheduling system that uses various other container scheduler backends (such as Kubernetes, docker swarm, and Red Hat OpenShift). It's primarily designed to make the cloud computing accessible to non-technical users such as radiologist and other people in the medical domain so that they could get analytical reports of the patient data in a fast and easy way.

## Motivation behind the Chris and why is it important?

* ChRIS allows researchers to focus more on their **analysis** rather than thinking about how to build the necessary compute architecture to achieve their analyses.
* In addition to that, ChRIS enables running the complex data analysis on **anywhere** such as local workstation, local compute clusters and the cloud without requiring the technical knowledge
* Moreover, it generates the patient analytics data in a **fast** and **anonymous** way easing the job of doctors and medical researchers. 

## 1. Vision and Goals Of The Project:

Plug-ins for ChRIS are primarily written in Python programming language along with operational parameters like the minimum number of GPUs, CPU, or RAM that are baked into the code. These plugin requirements are spesificed by the plugin developer and each plugin may have different computational requirements. But currently, the ChRIS system does not have the ability to check whether a certain plugin can be run on a selected compute environment. As a result, plugins may fail to run if their assigned compute environment does not satisfy its minimum requirements. Moreover, all the plugins that require the output of that failed plugin will also fail to run. The second problem in the ChRIS system is that, there is no automated way for assigning compute resources to plugins. However, in the ideal case, users should not bothered to choose the optimal way of assigning compute resources to their plugins. Becasue they may not know the answer of what is the best compute environment to run their analysis in a fastest way, or which computer resources should they use i they have x amount of budget in terms of US dollars? The third problem is that, the ChRIS system does not have descriptive fields in the database to define the specifications of the compute environment. Therefore, there is no information about the computational capacity of a compute resource inside the ChRIS backend.


Our goal for this project is to:
 * Develop a command-line application for the end-user to:
   *  determine the compute resource best fit for a plug-in based on two optimization functions: speed and monetary cost
   *  view the plug-in/pipeline's operational parameters/compute resources
   *  optimize a pipeline for cost or speed and report the correct compute resources required
   *  enable users to determine whether the remote environment satisfies the spec of the computational requirements of the computing pipeline requested by the users


 * Integrate the functionality of the command-line application into the ChRIS backend
   * Add a UI element to the web UI frontend (adding a compute resource called auto_free, etc.) to automatically choose a compute resource for a single plug-in
 

**Additional goals:**
* Create a plug-in for Banu Ahtam of the FNNDSC to calculate "subject age at time of scan" in a spreadsheet.

## 2. Users/Personas Of The Project

This project targets:

 * doctors, medical researchers, and scientific researchers will use ChRIS via a Graphical User Interface to efficiently perform cloud-based containerized computation.

 * admins of ChRIS, who are going to test or use the pipeline for generating analytical reports
 
For example, a doctor or radiologist can launch a workflow to analyze a set of MRI images of a patient, receive a technical report (like volume metric details of each part of the brain), and react accordingly.

## 3. Scope and Features Of The Project:

* Project Architecture:
    * ChRIS Project has three main components:

        * ChRIS UI which is a web interface for user interaction and creating analyses
        * ChRIS Backend for passing input data into the computing environment and receiving results from the computing environment
        
        * ChRIS Store for storing the descriptor JSON representation of plug-ins requested by the user in the front end. The backend sends a request to the plug-in manager (p-man), which tells the computer resource to start an instance


* By the end of this project, the users should be able to:
    
    * For a given plug-in (a created/written app that is containerized) and for a computing environment in which the plug-in is intended to run, check whether the resources are sufficient for the plug-in's requirements.

    * Given a registered pipeline, check whether all plug-ins in said pipeline are able to be executed in the selected compute environment.

    * For a collection of plug-ins in a registered pipeline and a given cost function (i.e., "speed," "monetary cost"), recommend each plug-in to the compute environment that satisfies its requirements.

    * View the number of GPUs, CPUs, or RAM of the compute resource directly in the ChRIS backend Django admin page.

    * Understand whether compute environment is sufficient or not to run the pipeline.

* The descriptors for a compute resource should be visible in the ChRIS REST API.
* The frontend should contain an "auto_free" (chooses the best compute resource with zero monetary cost) and "auto_best" (chooses the best compute resource with any monetary cost) compute environment that programmatically chooses the best environment for a plug-in.

# Future Work:

* Dynamic checking of remote compute resources for its capability.

* Add an option to define the amount of monetary budget for a plug-in
The current option we have are auto_free which is essentially a 0 budget and “auto_best” which is a infinite budget.
So we want the user to define a budget somewhere between 0 and infinity.

* Add user defined priority weighting.
For example, a user might want to focus more on number of CPUs or amount of memory.

* Extend our recommendation algorithm so that it covers the whole pipeline.

* Update our recommendation algorithm so that it depends on previous runtimes of the plug-in.
Instead of choosing the one with the most CPU, we can directly select the one with the lowest runtime


## 4. Solution Concept

Global Architectural Structure:

* A Python command-line application to fetch the current computing machine's hardware information from CUBE's REST API that can report:
  * any given pipeline's plug-ins
  * details of all compute resources, such as GPU, CPU, Cost, Memory
  * a check for whether the pipeline's compute resources are compatible with its plug-ins
  * a way to optimize any pipeline for cost, or speed
  * return all information as JSON for future implementation

* A frontend option, "auto_free" (chooses the best compute resource with zero monetary cost) and "auto_best" (chooses the best compute resource with any monetary cost) compute environment that programmatically chooses the best environment for a plug-in.
  * Pass any errors from backend to the frontend

Design Implication and Discussion:

* Python and Django are also intensively used in the ChRIS project backend. By using the same Django library, it is easier to maintain code.

  * Python is a powerful tool in the Linux environment. Hardware information and processing allocations could be done by correctly using Python.

## 5. Acceptance criteria

Minimum viable product:

* Having a command line interface to show the details of the compute resource
* Plug-in requirement checking for suitable compute resource
* Access the plug-ins of environment specs from the backend via the REST API

## 6. Release Planning

### Release 1 (by week 5): 
* Finished setting up the development environment
* Finish reading ChRIS documentation
* Figure out what specific service of the ChRIS project is responsible for the configuration of containers and how they interact with it.

### Release 2 (by week 7): 
* Start / continue exploring React JS
* Understand the ChRIS system and devise a solution to "discover" the specs of container that user intends to run their work on (check the plug-in's requirements)
* Start writing basic API that interacts with the app's plug-in requirements

### Release 3 (by week 9): 
* Draft a mockup/user interaction "dialogue" of the command line application to be built
* Start developing a command-line application that determines whether the current compute resources are sufficient/optimized to run the desired pipeline

### Release 4 (by week 11): 
* Finish developing a basic command-line application to get a pipeline's plug-ins and their computer resources
* Develop cost / speed functions for integration
* Finish the command line application by integrating cost/speed optimization
* Testing and prep for release

### Release 5 (by week 13): 
* Integrate the client into the ChRIS backend

### Final Release (by week 15):
* Deploy and release the product.
* Prepare the final presentation.

### Demos
[Demo 1](https://www.youtube.com/watch?v=kBIDokPnwpA)
[Demo 2](https://youtu.be/AWViu7jEWxQ)
[Demo 3](https://www.youtube.com/watch?v=9kYF9u7zSQE)
[Demo 4](https://www.youtube.com/watch?v=qEefKhnhthw)
[Demo 5](https://www.youtube.com/watch?v=kLuDLaTsvnM)
[Final Video](https://youtu.be/bQBsMb4K1CM)

### Commands
To bring up ChRIS Backend:
```
docker swarm leave --force &&                                                
docker swarm init --advertise-addr 127.0.0.1 &&                           
./unmake.sh ; sudo rm -fr CHRIS_REMOTE_FS; rm -fr CHRIS_REMOTE_FS; ./make.sh -U -I
```
To bring up ChRIS Frontend: (Assuming that backend is running at http://localhost:8000/api/v1/) 
```
docker run --rm -d --name chris_ui -p 3000:3000 -e REACT_APP_CHRIS_UI_URL=http://localhost:8000/api/v1/ ghcr.io/fnndsc/chris_ui:latest
```
Setup "auto_free" and "auto_best" compute environments:  
1. Visit the ChRIS admin page
```
http://localhost:8000/chris-admin
```
2. Click "Compute Resources"
3. Click "Add compute resource"
4. In the Name field, type "auto_free", or "auto_best"
5. The other parameters do not matter
6. Save

If you update chris-client and want to see the changes:
- Make sure you are in the ./chris-client-cli:
```
bash uninstall.sh
sudo bash install.sh
pip install .
```
