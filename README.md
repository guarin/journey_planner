# Robust Journey Planning

Robust journey planner for swiss public transport network taking possible delays into account. Detailed task description is in [project_description](project_description.md).

[final_notebook](notebooks/final_notebook.ipynb) explains the structure of the project.

A short video presenting the project can be found [here](https://www.youtube.com/watch?v=tZWT6d0ZCrg&feature=youtu.be).

**Installation**
```
conda env create -f local_environment.yml
jupyter labextension install @pyviz/jupyterlab_pyviz
```

If there are any issues run:
```
conda env create -f local_environment_export.yml
jupyter labextension install @pyviz/jupyterlab_pyviz
```

**Journey Planner Interface**
![](images/journey_planner.png)

**Journey Visualization**
![](images/journey_visualization.png)
