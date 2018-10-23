
nohup gunicorn -w 4 -b 0.0.0.0:5500 --pythonpath src  app:app  & echo $! > run.pid &
