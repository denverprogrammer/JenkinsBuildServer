
# Brings down all containers.
destroy:
	docker-compose down --remove-orphans --volumes

# Builds all of the dev containers and starts the server.  
# In your browser go to http://localhost to view webpage.
build:
	docker-compose up --build -d

password:
	docker exec -c `tail /var/jenkins_home/secrets/initialAdminPassword`
