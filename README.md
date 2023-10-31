# SCSE Dashboard

This folder concistst of the srouce code and raw data being used to implement the dashboard.

## Demo
To run the demo, please ensure that the environment is set up, the necessary libraries ad their dependencies are properly installed (follow the `requirements.txt` file). 
You may run ```streamlit run demo.py``` in the terminal to start the demo.   

  \* Some sample demo can be found in the `Sample` folder.
## Notes
The data are stored in mongoDB and queried based on specific function requirements. However, the connection string to my mongoDB is removed from this repo. For verification and future development purpose, I have exported all the data used for this project from mongoDB and save them to `data` as json objects.    


Have fun dashboarding!