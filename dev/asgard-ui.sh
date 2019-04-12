
container_id=$(docker run --rm -d \
                -p 4200:80 \
                -e ASGARD_API_BASE_URL=http://localhost:5000/ \
                -e SIEVE_LOGIN_REDIRECT=http://localhost:5000/login/google \
                --name asgard_ui \
                b2wasgard/asgard-ui:0.24.0)

echo "ASGARD UI (http://localhost:4200) container_id=${container_id:0:8}"
