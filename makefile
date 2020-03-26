# Need a way to cover up your mistakes?
# Does it need to be fast so that nobody will notice?
# Or do you need to just start from scratch ... a lot.
# Then this target is made for you.
NUKE_IT_NUKE_IT:
	make destroy
	docker volume prune --force
	docker network prune --force
	docker container prune --force
	docker rmi -f $(`docker images -aq`)

# Brings down all containers.
destroy:
		docker-compose down --remove-orphans --volumes

# Builds all of the dev containers and starts the server.  
# In your browser go to http://localhost to view webpage.
build:
	docker-compose up --build -d

password:
	docker exec -c `tail /var/jenkins_home/secrets/initialAdminPassword`

# Run unit tests agains slave.py
test:
	@python3 -m unittest discover docker/slave "*_test.py"
