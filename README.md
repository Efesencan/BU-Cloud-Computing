# BU-Cloud-Computing
** **

## 1. Vision and Goals Of The Project:

ChRIS (ChRIS Research Integration Service) ([ChRIS](http://chrisproject.org/)) is an active open source project, originally developed for analysis of medical imaging using High Performance Computers. However, it has pivoted to a more general and easy to use front end for doctors and other researchers to perform other computationally intensive medical related analyses with the help of cloud services. 

Plugins for ChRIS are written in Python with environment variables like number of GPUs, CPU threads, or amount of RAM baked into the code that the developer writes. Our goal for this project is to:
 * Develop a simple way for the end user to view (and change if necessary) the environment variables from the front end, bypassing the need for understanding and editing the code.

* Enable users to determine whether the remote environment satisfies the space of the environmental requirements of the pipeline.

## 2. Users/Personas Of The Project

ChRIS is used by doctors and medical researchers who deal with medical imaging of the brain and enables them to generate detailed analytical reports from these images using machine learning and cloud support. It can also be generalized to perform other compute intensive tasks such as analyzing COVID data or deep learning tasks. This project targets:

 * Medical researchers and doctors who will use ChRIS via Graphical User Interface

* Admins of the ChRIS, who are going to test or use the pipeline for generating analytical reports

## 3. Scope and Features Of The Project:

* By the end of this project, the users should be able to:
    
    * For a given plugin (a created/written app which is containerized), and for a compute environment in which the plugin is intended to run, check whether the resources are sufficient for the plugin’s requirements.

    * Given a collection of plugins which is  represented with graphs in ChRIS UI, check whether all plugins can be executed in the selected compute environment.

    * Addition and management of users of the system. 

    * For a collection of plugins in a graph, and for a given cost function (i.e: “fastest”, “cheapest”), assign each plugin to the compute environment that satisfies the   requirements for that plugin

    * View the number of GPUs, CPU threads, or amount of RAM directly from the workflow creator within the ChRIS project front end.
Increase/Decrease the parameters if desired.

    * Understand whether the space of the remote environment is sufficient or not to run the pipeline and generate analytical reports.

* The back end should access the plugins and the environmental requirements of the app and provide that information to the front end in a fast and efficient way.

* The API in the backend should be able to assign the plugins to the compute environment given the cost function in a most efficient way. 

* The back end should be able to feed information to the front end via an API on whether the defined environment was sufficient to run a plugin or pipeline (a series of plugins).

## 4. Solution Concept

A high-level outline of the solution…

* User interface written by ReactJS framework to  display relevant information.

* API written in Python to pass environment parameters to back end and post-execution information back to the front end

## 5. Acceptance criteria

Minimum acceptance criteria is having an interface showing the details of the compute environment Stretch goals are:

* User should be able to select the computing environment from multiple “preset” of computing environment

* For a collection of plugins in a graph, and for a given cost function (i.e: “fastest”, “cheapest”), assigning each plugin to the compute environment that satisfies the requirements for that plugin

* Having a backend API for adjusting/customizing these computing environments.

## 6. Release Planning

### Release 1 (by week 5): 
* Finish user stories
* Finished setting up development environment
* Finish reading ChRIS documentation

### Release 2 (by week 7): 
* Figure out what specific service of the ChRIS project is responsible for configuration of containers and how they interact with it.

### Release 3 (by week 9): 
* Find a way for ChRIS system to “discover” the specs of container that user intends to run their work on (check the plugin’s requirements)

### Release 4 (by week 11): 
* Develop a basic API for communicating user’s “plug-ins” requirement to the container scheduler

### Release 5 (by week 13): 
* Develop a basic API for relaying/reporting the possible mismatch of plug-in specifications’ requirement and user’s working environment

### Final Release (by week 15):
* Develop front end for user to see and interact with the environment information


