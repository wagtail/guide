# Guide

A website to teach Wagtail CMS to content editors, moderators and administrators.

Wagtail guide brings you:
- Tutorials, 
- How-to, 
- Reference 
- Background information

## Google Summer of Code

This project is a part of Google Summer of Code 2022 under the organization [**Wagtail**](https://wagtail.org/).

## Development

### Frontend

- Setup the appropriate version of node.    
`nvm use`   
The node version shoule be `v16.*`. You can check it by running 
`node -v`   
- Install all the dependencies     
`yarn`  
- Compile the frontend by running       
`yarn start`    
For production build run    
`yarn start`    

### Backend
- Verify that your python version is `3.9.*` by running     
`python -V` 
- Setup virtual environment     
    ``` bash
    python -m venv env
    source env/bin/activate
    ```     
- Install the required dependencies     
`python -m pip install requirements.txt`    
- Apply migrations  
    `python manage.py migrate`  
- Create a super-user   
`python manage.py createsuperuser`  
- Start the server  
`python manage.py runserver`    
