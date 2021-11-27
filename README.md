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
 * Develop a command line application for the end user to:
   *  determine a compute resource's environment programatically   
   *  view the plug-in / pipeline’s operational variables/compute resources from the front end
   *  optimize a pipeline for cost, or speed and report the correct compute resources required

 * Add a UI element to ChRIS_ui to automatically choose a compute resource for a single plugin
 

* Enable users to determine whether the remote environment satisfies the spec of the computational requirements of the computing pipeline requested by the users

**Additional goals:**
* Create a plugin for Banu Ahtam of the FNNDSC to calculate "subject age at time of scan" in a spreadsheet.

## 2. Users/Personas Of The Project

This project targets:

 * Doctors, Medical researchers, and scientific researchers who will use ChRIS via a Graphical User Interface to easily perform cloud-based containerized computation.

 * Admins of ChRIS, who are going to test or use the pipeline for generating analytical reports
 
 * For example, a doctor or radiologist can launch a workflow to analyze a set of MRI images of a patient, receive a technical report (like volume metric details of each part of the brain), and react accordingly

## 3. Scope and Features Of The Project:

* Project Architecture:
    * ChRIS Project has 3 main components:

        * ChRIS Backend for passing input data into computing environment, and receiving results from the computing environment
        
        * ChRIS Store for storing the descriptor JSON representation of plugins which are then requested by the user in the front end. The backend sends a request to the plugin manager (p-man) which tells the computer resource to start an instance

        * Containerized Plug-ins managed by OpenShift
        
        * Multiple Computing environments managed by OpenStack

* By the end of this project, the users should be able to:
    
    * For a given plugin (a created/written app which is containerized), and for a compute environment in which the plugin is intended to run, check whether the resources are sufficient for the plugin’s requirements.

    * Given a collection of plugins which is represented with graphs in ChRIS UI, check whether all plugins can be executed in the selected compute environment.

    * For a collection of plugins in a graph, and for a given cost function (i.e: “fastest”, “cheapest”), assign each plugin to the compute environment that satisfies the   requirements for that plugin

    * View the number of GPUs, CPU threads, or amount of RAM directly from the workflow creator within the ChRIS project front end.

    * Understand whether the space of the remote environment is sufficient or not to run the pipeline and generate analytical reports.

* The command line application should be able compute environment given the cost or speed function. 

* The backend should be able to feed via the REST API, the descriptor for any compute resource.
* The frontend should contain an "auto" compute environment that programmatically chooses the best environment for a plugin.

# Not Guaranteed:

* Checking local computing resources for a list of computing nodes (iterative design);

* Designing algorithms to create different computing resources allocation plans (e.g. Best Performance Plan and Cost Effective Plan);

* Optimize allocation plans for different types of chipsets (e.g. Different resource allocation method for Intel, NVIDIA, or AMD);


## 4. Solution Concept

Global Architectural Structure:

* User interface written by ReactJS framework to  display relevant information

* A Python command line application to fetch the current computing machine’s hardware information from CUBE's REST API that can report:
  * Any given pipeline's plugins
  * Details of all compute resources, such as GPU, CPU, Cost, Memory
  * A check for whether the pipeline's compute resources are compatible
  * A way to optimize any pipeline for cost, or speed
  * Return all information as JSON for future implementation

* Pass post-execution information from backend to the frontend

Design Implication and Discussion:

* ReactJS enables Cross Platform Development. This could make the frontend more volatile and usable across different platforms;

* ReactJS is also the frontend development environment of the ChRIS project. This makes our front end more integratable to the main dashboard;

* Python and Django is also intensively used in the ChRIS project backend. By using the same Django library, it is easier to maintain code.

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
* Draft a mockup/user interaction "dialogue" of the command line application to be built
* Start developing command line application that determines whether the current compute resources are sufficient/optimized to run the desired pipeline

### Release 4 (by week 11): 
* Finish developing a basic command line application to get a pipeline's pluging and their computer resources
* Develop cost / speed functions for integration
* Finish the command line application by integrating cost/speed optimization
* Testing and prep for release

### Release 5 (by week 13): 
* Integrate the client into the ChRIS Frontend

### Final Release (by week 15):
* Deploy and release the product.
* Prepare the final presentation.

### Demos
[Demo 1](https://www.youtube.com/watch?v=kBIDokPnwpA)
[Demo 2](https://youtu.be/AWViu7jEWxQ)
[Demo 3](https://www.youtube.com/watch?v=9kYF9u7zSQE)
[Demo 4](https://www.youtube.com/watch?v=qEefKhnhthw)

### Commands
To bring up ChRIS Backend:
```
docker swarm leave --force &&                                                
docker swarm init --advertise-addr 127.0.0.1 &&                           
./unmake.sh ; sudo rm -fr CHRIS_REMOTE_FS; rm -fr CHRIS_REMOTE_FS; ./make.sh -U -I
```



