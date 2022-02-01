# JBI100-example-app

## About this app

The tool provides different visualizations, with the goal of supporting the user to discover or explore whether 
certain factors contribute to the number of road accidents that happen in Great Britain. The application will 
mainly focus on the user: Government personnel.

### Libraries
* Python(Dash), HTML and CSS for interaction and layout
* Pandas for data processing and manipulation
* Scikit-learn for data analysis
* Plotly-express for generating visualization and built-in chart interactions.

## Requirements

* Python 3 (add it to your path (system variables) to make sure you can access it from the command prompt)
* Git (https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)

## Dataset source
All datasets used in the project was taken from the Road Safety Data collected by Data.gov.uk(Department of Transport)
More specifically, Road safety data - Accidents 1979-2020. Below is the link to it.
https://data.gov.uk/dataset/cb7ae6f0-4be6-4935-9277-47e5ce24a11f/road-safety-data

## How to run this app

We suggest you to create a virtual environment for running this app with Python 3. 
Unzip the submitted zip file containing project source code.

```
> cd <folder name on your computer>
> python -m venv venv

```
If python is not recognized use python3 instead

In Windows: 

```
> venv\Scripts\activate

```
In Unix system:
```
> source venv/bin/activate
```

Install all required packages by running:
```
> pip install -r requirements.txt
```

Run this app locally with:
```
> python app.py
```
You will get a http link, open this in your browser to see the results. You can edit the code in any editor (e.g. Visual Studio Code) and if you save it you will see the results in the browser.

## Resources

* [Dash](https://dash.plot.ly/)
* [Plotly](https://plotly.com/python/plotly-express/)
* [Scikit-learn](https://scikit-learn.org/stable/)
* [Pandas](https://pandas.pydata.org/)
