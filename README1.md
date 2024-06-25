#Steps to Run:
#In windows:
#From Ubuntu Shell:
sudo service redis-server start
#From command prompt
venv\Scripts\activate
pip install --no-cache-dir -r <project_dir>\backend\requirements.txt
#From project directory
python -m unittest discover test

cd backend
python app_run.py

#From another terminal in angular-app directory 
npm install -g http-server
http-server . -p 8080
#Front end will run

#To check the asynchronous insert_order
#From backend directory
python Subscriber.py
#From another directory
python Resource_test.py

#To test the docker
#start docker engine
#From Ubuntu shell
sudo service redis-server stop
#From command prompt
 net stop MySQL80
#From backend dir
docker-compose up --build --force-recreate

#Run the front end again and check the app


#To deploy it in kuberante
minikube start
& minikube -p minikube docker-env --shell powershell | Invoke-Expression
docker build -t flask-app:latest .
kubectl apply -f deployment.yaml

#to make it scalable
minikube service flask-app-service
kubectl scale deployment flask-app-deployment --replicas=<no_of_replica_you want>

#To monitor the application
kubectl get pods
kubectl describe pod <pod-name>








