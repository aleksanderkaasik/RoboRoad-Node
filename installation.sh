for item in $(cat package.txt); do
    apt install -y $item
done

$domain=$1

URL="http://$domain/api/add"

$data="{ 
        \"NodeName\": \"$2\",
        \"NodeAddress\": \"$3\"
    }"

curl -X POST $URL \
     -H "Accept: application/json" \
     -H "Content-Type: application/json" \
     -d "$data"