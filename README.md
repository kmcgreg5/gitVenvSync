# gitVenvSync

### Description
---
A python script for updating and syncing github repositories and python virtual environments using pipreqs and GitPython.
Utilizes GitHub token authentication over HTTPS.


### Usage
---
Run the script with no arguments to initialize it's python virtual environment, it will exit afterwards and you can run it with proper parameters

```
python gitVenvSync.py
```


### The CLI options are as follows:
---

```
python gitVenvSync.py [--force|--clean] github-username repo-name
```

The ```--force``` and ```--clean``` option both create a fresh python virtual environment for the code repository. 
The ```---force---``` option then updates solely from a requirements.txt file in the code repository. 
The ```---clean---``` option instead merges the requirements.txt file from the repository and a pipreqs scan of the code repository, as is the normal procedure.


### Bash script example
---

```
#!/bin/bash
cd /repo-directory
source penv/bin/activate
python gitVenvSync.py kmcgreg5 SonarrScripts
deactivate

cd code
source penv/bin/activate
python unmonitor-downloaded-episodes.py BASE_URL API_KEY
deactivate
```
