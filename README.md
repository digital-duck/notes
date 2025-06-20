# notes
simple note-taking app in 

## [alpine.js](https://alpinejs.dev/) 
- [src](https://github.com/alpinejs/alpine)
- [doc](https://alpinejs.dev/start-here)


### setup

```
cd alpine
conda create -n ui python=3.12 
conda activate ui
pip install -r requirements.txt

# launch 

# python main.py 

uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Open browser at http://localhost:8000
```


## streamlit

- [docs](https://docs.streamlit.io/get-started/fundamentals/main-concepts)

### setup
```
cd streamlit
pip install -r requirements.txt
streamlit run st_note.py

# open browser at http://localhost:8501/
```