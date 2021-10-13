# Enabling Real-world Medical Compute Workflows on the Cloud (and others) to aid in Clinical Decision Making
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

## 1. Vision and Goals Of The Project:

ChRIS (ChRIS Research Integration Service) ([ChRIS](http://chrisproject.org/)) is an active open source project, developed from inception as a platform to facilitate the execution of complex (research focused) compute operations by non technical users. It's genesis arose from a realization that considerable programs of value exist in the research world and the observation that most (if not all) of these programs are rarely used by anyone other than the original authors. ChRIS, at its heart, is a platform that attempts to cross this divide. It has currently grown into a container based scheduling system that uses various other container scheduler backends (such as kubernetes, docker swarm, and Red Hat OpenShift).

Plugins for ChRIS are mostly written in Python with operational variables like number of GPUs, CPU threads, or amount of RAM baked into the code that the developer writes. Our goal for this project is to:
 * Develop a simple way for the end user to view the plug-in / pipeline’s operational variables from the front end.

* Enable users to determine whether the remote environment satisfies the spec of the computational requirements of the computing pipeline requested by the users

## 2. Users/Personas Of The Project

This project targets:

 * Doctors, Medical researchers, and scientific researchers who will use ChRIS via a Graphical User Interface to easily perform cloud-based containerized computation.

 * Admins of ChRIS, who are going to test or use the pipeline for generating analytical reports
 
 * For example, a doctor or radiologist can launch a workflow to analyze a set of MRI images of a patient, receive a technical report (like volume metric details of each part of the brain), and react accordingly

## 3. Scope and Features Of The Project:

* Project Architecture:
    * ChRIS Project has 3 main components:

        * ChRIS Backend for passing input data into computing environment, and receiving results from the computing environment
        
        * ChRIS Store for storing the descriptor JSON representation of plugins which are then requested by the user in the front end and the backend sends a request to start an instance

        * Containerized Plug-ins managed by OpenShift
        
        * Multiple Computing environments managed by OpenStack

* By the end of this project, the users should be able to:
    
    * For a given plugin (a created/written app which is containerized), and for a compute environment in which the plugin is intended to run, check whether the resources are sufficient for the plugin’s requirements.

    * Given a collection of plugins which is  represented with graphs in ChRIS UI, check whether all plugins can be executed in the selected compute environment.

    * For a collection of plugins in a graph, and for a given cost function (i.e: “fastest”, “cheapest”), assign each plugin to the compute environment that satisfies the   requirements for that plugin

    * View the number of GPUs, CPU threads, or amount of RAM directly from the workflow creator within the ChRIS project front end.

    * Understand whether the space of the remote environment is sufficient or not to run the pipeline and generate analytical reports.

* The backend should access the plugins and the environmental requirements of the app and provide that information to the front end in a fast and efficient way.

* The backend should be able to assign the plugins to the compute environment given the cost function in a most efficient way. 

* The backend should be able to feed information to the front end via an API on whether the defined environment was sufficient to run a plugin or pipeline (a series of plugins).

# Not Guaranteed:

* Checking local computing resources for a list of computing nodes (iterative design);

* Designing algorithms to create different computing resources allocation plans (e.g. Best Performance Plan and Cost Effective Plan);

* Optimize allocation plans for different types of chipsets (e.g. Different resource allocation method for Intel, NVIDIA, or AMD);

* Support for graphics card hot swap.

* Full support for vGPU assignment and GPU PCI device assignment


## 4. Solution Concept

Global Architectural Structure:

* User interface written by ReactJS framework to  display relevant information

* Use Shell Script, Linux commands, Python,  or OpenCL to fetch the current computing machine’s hardware information and reallocate the cores for different computation plans

* Pass post-execution information from backend to the frontend

Design Implication and Discussion:

* ReactJS enables Cross Platform Development. This could make the frontend more volatile and usable across different platforms;

* ReactJS is also the frontend development environment of the ChRIS project. This makes our front end more integratable to the main dashboard;

* Python and PyFlask is also intensively used in the ChRIS project backend. By using the same PyFlask library, it is easier to maintain code.

* Shell Script is a powerful tool in the Linux environment. Hardware information and processing allocations could be done by correctly using shell script.

## 5. Acceptance criteria

Minimum acceptance criteria is having an interface showing the details of the compute environment Stretch goals are:

* Having an interface showing the details of the environment

* Access the plugins of environment specs from the backend via the REST API in an efficient way

## 6. Release Planning

### Release 1 (by week 5): 
* Finished setting up development environment
* Finish reading ChRIS documentation
* Figure out what specific service of the ChRIS project is responsible for configuration of containers and how they interact with it.

### Release 2 (by week 7): 
* Start / continue exploring React JS
* Understand the ChRIS system and devise a solution to “discover” the specs of container that user intends to run their work on (check the plugin’s requirements)
* Start writing basic API that interacts with the app’s plugin requirements

### Release 3 (by week 9): 
* Develop API that determines whether the current environment space is sufficient to run the desired pipeline
* Start developing GUI to show and choose the specs.

### Release 4 (by week 11): 
* Develop a basic API for relaying/reporting the possible mismatch of plug-in specifications’ requirement and user’s working environment
* Keep working/improving on the UI part

### Release 5 (by week 13): 
* Develop an API that can assign the optimal work space to the application under certain cost functions.
* Keep working/improving on the UI part

### Final Release (by week 15):
* Deploy and release the product.
* Prepare the final presentation.

### Demos
[Demo 1](https://www.youtube.com/watch?v=kBIDokPnwpA)
[Demo 2](https://youtu.be/AWViu7jEWxQ)



