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

## What is the ChRIS project?

ChRIS (ChRIS Research Integration Service) ([ChRIS](http://chrisproject.org/)) is an active open-source distributed data and computation framework, developed from inception as a platform to facilitate the execution of complex (research-focused) compute operations by non-technical users. Its genesis arose from a realization that considerable programs of value exist in the research world and the observation that most (if not all) of these programs are rarely used by anyone other than the original authors. ChRIS, at its heart, is a platform that attempts to cross this divide. It has grown into a container-based scheduling system that uses various other container scheduler backends (such as Kubernetes, docker swarm, and Red Hat OpenShift). It is primarily designed to make cloud computing accessible to non-technical users such as radiologists and other people in the medical domain to get analytical reports of the patient data in a fast and easy way.

## Motivation behind ChRIS and why it is important:

* ChRIS allows researchers to focus more on their **analysis** rather than thinking about how to build the necessary compute architecture to achieve their analyses.
* In addition, ChRIS enables running the complex data analysis on **anywhere** such as a local workstation, local compute clusters, and the Cloud without requiring the technical knowledge.
* Moreover, it generates the patient analytics data in a **fast** and **anonymous** way, easing the job of doctors and medical researchers. 

## 1. Vision and Goals Of The Project:

Plug-ins for ChRIS are primarily written in Python programming language along with operational parameters like the minimum number of GPUs, CPU, or RAM that are baked into the code. The plug-in developer specifies these plug-in requirements, and each plug-in may have different computational requirements. However, currently, the ChRIS system does not have the ability to **check** whether a particular plug-in can be run on a selected compute environment. As a result, plug-ins may **fail** to run if their assigned compute environment does not satisfy its minimum requirements. Moreover, all the plug-ins that require the output of that failed plug-in will also fail to run. The second problem in the ChRIS system is that there is no automated way for **assigning** compute resources to plug-ins. However, in the ideal case, end-users should not be bothered to choose the optimal way of assigning compute resources to their plug-ins because they may not know the answer of the best compute environment to run their analysis in the fastest way or based on their monetary budget. The third problem is that the ChRIS system does not have descriptive fields in the database to define the specifications of the compute environment. Therefore, there is no information about the computational capacity of a compute resource inside the ChRIS backend.

Our goal for this project is to:
 * Expand the fields of "compute environments" in the database to include more fields that describe the characteristics of a compute environment.
   * Ex fields: Total # of CPU, total # of GPU, CPU clock speed, # of workers, the total amount of memory, cost of that compute environment, etc.,   
 * Develop a command-line interface application for the ChRIS admins and developers to:
   *  determine the compute resource that best fits for a plug-in based on two optimization functions: speed and monetary cost
   *  view the plug-in/pipeline's operational parameters/compute resources and their details
   *  optimize a pipeline for cost or speed and report the correct compute resources required
   *  enable ChRIS admin's to determine whether the remote environment satisfies the spec of the computational requirements of the computing pipelines that may be requested by end-users

 * Integrate the functionality of the command-line application into the ChRIS backend so that it is also available to the public (non-technical users, medical researchers, etc.)
   * Add a UI element to the web UI frontend (adding a compute resource called auto_free, auto_best, etc.) to automatically choose a compute resource for a single plug-in
   * Display error message in the ChRIS UI when there is no compute environment that satisfies the plug-in requirements and return an error message explaining why that is the case.
      * Example error message: The plug-in required at least 200 MB of memory; however, the compute environment (ex. host) has only 100 MB available.    

**Additional goals:**
* Create a plug-in for Banu Ahtam of the FNNDSC to calculate "subject age at time of scan" in a spreadsheet.

## 2. Users/Personas Of The Project

This project targets:

 * doctors, medical researchers, and scientific researchers who will use ChRIS via a Graphical User Interface to efficiently perform cloud-based containerized computation.
    * These users will use the web frontend elements ("auto_free"/"auto_best") to quickly choose a compute resource for a plugin.  

 * admins of ChRIS, who are going to test or use the plug-in for generating analytical reports
    * These admins are also able to use the web frontend elements. However, the admins can also use the command line program to run tests and perform actions like listing plugins, and checking whether compute resources are compatible with a plug-in.
 
For example, a doctor or radiologist can launch a workflow to analyze a set of MRI images of a patient, receive a technical report (like volume metric details of each part of the brain), and react accordingly.

## 3. Scope and Features Of The Project:

* Project Architecture:
    * ChRIS Project has three main components:

        * ChRIS UI, which is a web interface for user interaction and creating analyses
        * ChRIS Backend for passing input data into the computing environment and receiving results from the computing environment
        
        * ChRIS Store stores the descriptor JSON representation of plug-ins requested by the user in the front end. The backend sends a request to the plug-in manager (p-man), which tells the computer resource to start an instance


* By the end of this project, the users should be able to:
    
    * For a given plug-in (a created/written app that is containerized) and for a computing environment in which the plug-in is intended to run, check whether the resources are sufficient for the plug-in's requirements.

    * For a collection of plug-ins in a registered pipeline and a given cost function (i.e., "speed," "monetary cost"), recommend each plug-in to the compute environment that satisfies its requirements.

    * View the number of GPUs, CPUs, or RAM of the compute resource directly in the ChRIS backend Django admin page.

    * Understand whether compute environment is sufficient or not to run the pipeline. If not, report what the problem was. 

* The descriptors for a compute resource should be visible in the ChRIS REST API.
* The frontend should contain an option named "auto_free" (chooses the best compute resource with zero monetary cost) and "auto_best" (chooses the best compute resource with any monetary cost) compute environment, which allows choosing the best environment for a plug-in in an automated way.

# Future Work:

* Dynamic checking of remote compute resources for its capability.

* Add an option to define the amount of monetary budget for a plug-in. 
The current options we have are auto_free, essentially a 0 budget, and "auto_best," which is an infinite budget.
So we want the end-user to define a budget somewhere between 0 and infinity.

* Add user-defined priority weighting.
For example, a user might want to focus more on the number of CPUs or memory. However, we currently have a fixed formulation for selecting the best compute environment for a plug-in. 
* Extend our recommendation algorithm to cover the whole pipeline instead of a single plug-in.

* Update our recommendation algorithm to depend on the previous runtime history of the plug-ins rather than a fixed formulation.
Instead of choosing the one with the highest CPU and CPU clock speed, we can directly select the lowest runtime.


## 4. Solution Concept

Global Architectural Structure:

* A Python command-line application to fetch the current computing machine's hardware information from CUBE's REST API that can report:
  * any given pipeline's plug-ins
  * details of all compute resources, such as GPU, CPU, Cost, Memory
  * a check for whether the pipeline's compute resources are compatible with its plug-ins
  * a way to optimize any pipeline for cost, or speed
  * return all information as JSON for future implementation

* A frontend option, "auto_free" (chooses the best compute resource with zero monetary cost) and "auto_best" (chooses the best compute resource with any monetary cost) compute environment that programmatically chooses the best environment for a plug-in.
  * Pass any errors from the backend to the frontend

Design Implication and Discussion:

* Python and Django are also intensively used in the ChRIS project backend. Using the same Django library makes it easier to implement and maintain the code.

## 5. Acceptance criteria

Minimum viable product:

* Having a command-line interface tool to show the details of the compute resources, plug-ins, pipelines
* Requirement checking of a plug-in to determine whether the intended compute environment satisfies the plug-ins needs. 
* Access the plug-ins of environment specs from the backend via the REST API

## 6. Release Planning

### Release 1 (by week 5): 
* Finished setting up the development environment
* Finish reading ChRIS documentation
* Figure out what specific service of the ChRIS project is responsible for the configuration of containers and how they interact with it.

### Release 2 (by week 7): 
* Start / continue exploring React JS
* Understand the ChRIS system and devise a solution to "discover" the specs of container that end-user intends to run their work on (check the plug-in's requirements)
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
2. Click "Compute Resources."
3. Click "Add compute resource."
4. In the Name field, type "auto_free" or "auto_best."
5. The other parameters do not matter
6. Save

If you update chris-client and want to see the changes:
- Make sure you are in the ./chris-client-cli:
```
bash uninstall.sh
sudo bash install.sh
pip install .
```
