for item in $(cat package.txt); do
    apt install -y $item
done